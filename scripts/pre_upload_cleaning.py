'''
RUN THIS FILE IF YOU HAVE TO UPLOAD DATA THAT MEETS FIGURE 2a (in INSTRUCTION MANUAL) SCHEMA!!!!!

Reads in csv files that are in original schema (Figure 2a in Instruction Manual), 
converts them to updated schema (Figure 2b), 
then uploads new data to database

'''


import pandas as pd
import numpy as np
import datetime as dt
import nltk, re, string
import math as m
import sklearn
import pytz
from datetime import datetime
from django.utils.dateparse import parse_date
from website.models import Response, Question, ResponseOptions, Survey, DocketCharge, DocketProceeding
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import pairwise_distances

def run():

	# get DF's for each object as given in original schema
	# YOU MIGHT HAVE DIFFERENT FILE NAMES
	response_unclean_df = pd.read_csv("./data/cwn/2019.to.2021.responses.exported.before.cleaning.csv" ,encoding = "latin1")
	response_clean_df = pd.read_csv("./data/cwn/2019.to.2021.responses.exported.after.cleaning.csv",encoding = "latin1")
	response_options_df = pd.read_csv("./data/cwn/all.response.options.csv",encoding = "latin1")
	questions_df = pd.read_csv("./data/cwn/all.questions.csv",encoding = "latin1")
	surveys_df = pd.read_csv("./data/cwn/all.surveys.csv", encoding="latin1")


	def cleanText(doc):
		#Removes punctuation, numbers, stopwords
		#Returns tokenized form
		stopword = nltk.corpus.stopwords.words('english')
		
		regex = r'style="font-size: \d+pt; line-height: \d+%; font-family: \w+;"'
		doc = re.sub(regex,"",doc)
		
		no_nums = "".join([char for char in doc if not char.isdigit()])
		regex = r'<\w+>|<\\w+>|</\w+>'
		
		regex_2 = r'span|underline|'
		
		no_nums = re.sub(regex,"",no_nums)
		no_nums = re.sub(regex_2,"",no_nums)
		
		no_punc = "".join([char.lower() for char in no_nums if char not in string.punctuation])
		regex_3 = r'styletextdecoration'
		no_punc = re.sub(regex_3,"",no_punc)
		
		#remove single character from question number
		no_punc =  ' '.join( [w for w in no_punc.split() if len(w)>1] )
		
		#remove special characters due to latin-1
		no_punc = unicodedata.normalize('NFKD', no_punc).encode('ascii', 'ignore')
		no_punc = no_punc.decode('utf-8')

		
		return no_punc

	def add_cluster_id_to_Question():
		vectorizer = CountVectorizer(analyzer='word', 
								 #only words with 3 or more char
								  token_pattern=r'\b[a-zA-Z]{3,}\b',  
								  ngram_range=(1, 2), 
								 #3 times at least
								 min_df = 3)
		vectorized = vectorizer.fit_transform(questions_df["clean.text"])

		df_counts = pd.DataFrame(vectorized.toarray(), 
					index=['sentence '+str(i) 
						   for i in range(1, 1+len(questions_df["clean.text"]))],
					columns=vectorizer.get_feature_names_out())
		tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
		vectorized_tfidf = tfidf_transformer.fit_transform(vectorized)

		df_tfidf = pd.DataFrame(vectorized_tfidf.toarray(), 
					 index=['sentence '+str(i) 
							for i in range(1, 1+len(questions_df["clean.text"]))],
					 columns=vectorizer.get_feature_names_out())
		cosine_sim = pairwise_distances(df_tfidf, metric='cosine')

		#closer the cosine value to 0, the greater the match between vectors
		df_cosine_sim = pd.DataFrame(cosine_sim, columns = questions_df["question.id"])
		df_cosine_sim = df_cosine_sim.set_index(questions_df["question.id"])

		cluster_set_mappings = {}


		for i in df_cosine_sim.index:
			temp = df_cosine_sim.loc[i]  #give dfs for every sentence
			temp = temp[(temp < 0.3) == True]
			temp = temp.to_frame()
			values_question_ids = temp.apply(lambda row: row[row == 'question.id'].index.to_list(), axis = 1)
			values_question_ids = values_question_ids.to_dict()
			cluster_set_mappings[i] = list(values_question_ids.keys())


		cluster_ids = dict() # maps question_id to cluster id
		seen = set()

		cluster_id = 0
		for key in cluster_set_mappings:
			q_ids = [int(key)] + list(cluster_set_mappings[key])
			for q_id in q_ids:
				if q_id in seen:
					continue
				cluster_ids[q_id] = cluster_id
				seen.add(q_id)
			cluster_id += 1
		questions_df['cluster.id'] = questions_df.apply(lambda row: cluster_ids[row['question.id']], axis=1)

	def add_choice_text_to_Response():
		mapping = {k:v for k,v in zip(response_options_df['choice.id'], response_options_df['response.option.text'])}
		mapping1 = {k:v for k,v in zip(mapping.keys(), mapping.values()) if m.isnan(k) == False}
		mapping1[float('nan')] = float('nan')
		response_clean_df["choice_text"] = response_clean_df['choice_id'].map(mapping1)


	# Question modifications
	# -----------------------

	# ADD question_clean_text
	questions_df['clean.text'] = questions_df["question.text"].apply(lambda x: cleanText(str(x)))

	# ADD cluster_id 
	add_cluster_id_to_Question()
	# ------------------------

	# Response modifications
	# ----------------------

	# ADD choice_text
	add_choice_text_to_Response()

	# ADD choice_clean_text
	response_clean_df['clean.res.choice.text'] = response_clean_df["choice_text"].apply(lambda x: cleanText(str(x)))

	questions_df = questions_df.loc[:, ~questions_df.columns.str.contains('^Unnamed')]
	response_clean_df = response_clean_df.loc[:, ~response_clean_df.columns.str.contains('^Unnamed')]
	surveys_df = surveys_df.loc[:, ~surveys_df.columns.str.contains('^Unnamed')]
	response_options_df = response_options_df.loc[:, ~response_options_df.columns.str.contains('^Unnamed')]

	# SURVEYS
	# --------
	# WORKS

	print("Beginning Surveys")
	for index, row in surveys_df.iterrows():
		fields = [int(x) if (i == 1 and len(str(x)) == 6) else 0 if (i == 1) else x if (type(x) != float) else 0 for i, x in enumerate(list(row))]
		Survey.objects.create(survey_id=fields[0], survey_year=fields[1], survey_name=fields[2],
	 						survey_use_start_date=fields[3], survey_use_end_date=fields[4],
	 						survey_phase_id=fields[5], survey_phase_venue_type=fields[6],
	 						survey_part_id=fields[7], survey_observation_level=fields[8],
	 						observer_type=fields[9], court_id=fields[10], survey_notes=fields[11])
	print("Done Surveys {}".format('\n'*3))


	print("Beginning Questions")
	# QUESTIONS
	# ----------
	# transfer question csv/df to database
	# WORKS
	for index, row in questions_df.iterrows():
		fields = [x if type(x) != float else 0 for x in list(row)]
		print(fields[1])
		print(fields[5])
		Question.objects.create(question_id=fields[0], question_text=fields[1], question_type=fields[2], 
								question_subtype=fields[3], survey=Survey.objects.get(survey_id=fields[4]),
								question_clean_text=fields[5], cluster_id=fields[6])
	print("Done Questions {}".format('\n'*3))


	print("Beginning ResponseOptions")
	# # RESPONSE_OPTIONS
	# # ----------------
	# # transfer responseOption csv/df to database
	# # WORKS
	for index, row in response_options_df.iterrows():
		fields = [row[i] if (type(row[i]) != float or (i == 5 or i == 3)) else 0 for i in range(len(list(row)))] 
		# unpack an iterable with '*'

		ResponseOptions.objects.create(response_option_id=fields[0], survey=Survey.objects.get(survey_id=fields[1]), question=Question.objects.get(question_id=fields[2]), 
	 									row_id=fields[3], row_text=fields[4], choice_id=fields[5], 
										response_option_text=fields[6])

	print("Done ResponseOptions {}".format('\n'*3))




	print("Beginning Responses")
	# RESPONSES
	# ----------
	# transfer response csv/df to database
	# WORKS

	for index, row in response_clean_df.iterrows():
		# we use 0 instead of np.nan because IntegerField's cannot take nans
		fields = [row[i] if (type(row[i]) != float or (5 <= i <= 6)) else 0 for i in range(len(list(row)))]
		# some data validation for length of str fields
		fields[3] = str(fields[3])[:5000]
		fields[8] = str(fields[8])[:200]

		r = Response.objects.create(survey=Survey.objects.get(survey_id=fields[0]), collector_id=fields[1], responder_id=fields[2],
								question=Question.objects.get(question_id=fields[4]), response_text=fields[3], 
								row_id=fields[5], choice_id=fields[6], other_id=fields[7], choice_text=fields[8],
								choice_clean_text=str(fields[9]))


	print("Done Responses {}".format('\n'*3))
	






