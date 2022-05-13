'''
RUN THIS FILE IF YOU HAVE TO UPLOAD DATA THAT MEETS FIGURE 2b (in INSTRUCTION MANUAL) SCHEMA!!!!!

'''

import pandas as pd
import numpy as np
import pytz
from datetime import datetime
from django.utils.dateparse import parse_date
from website.models import Response, Question, ResponseOptions, Survey, DocketCharge, DocketProceeding

def run():

	# delete all initial data
	#Response.objects.all().delete()
	#Question.objects.all().delete()
	#ResponseOptions.objects.all().delete()
	#Survey.objects.all().delete()

	# YOU MIGHT HAVE DIFFERENT FILE NAMES

	responses_df = pd.read_csv('./scripts/data/responses_cleaned_2_sarah_nlp.csv', encoding='latin1')
	questions_df = pd.read_csv('./scripts/data/all.questions.cleaned.with_clusters.csv', encoding='latin1')
	response_options_df = pd.read_csv('./scripts/data/all_response_options.csv', encoding='latin1')
	surveys_df = pd.read_csv('./scripts/data/all.surveys.csv', encoding='latin1')

	questions_df = questions_df.loc[:, ~questions_df.columns.str.contains('^Unnamed')]
	response_clean_df = response_clean_df.loc[:, ~response_clean_df.columns.str.contains('^Unnamed')]
	surveys_df = surveys_df.loc[:, ~surveys_df.columns.str.contains('^Unnamed')]
	response_options_df = response_options_df.loc[:, ~response_options_df.columns.str.contains('^Unnamed')]

	'''
	responses_df = pd.read_csv('/mnt/c/Users/victo/OneDrive/Documents/Github/heroku-dashboard-4020/scripts/data/responses_cleaned_2_sarah_nlp.csv', encoding='latin1', index_col=0)

	questions_df = pd.read_csv('/mnt/c/Users/victo/OneDrive/Documents/Github/heroku-dashboard-4020/scripts/data/all_questions_cleaned_with_clusters.csv', encoding='latin1')

	response_options_df = pd.read_csv('/mnt/c/Users/victo/OneDrive/Documents/Github/heroku-dashboard-4020/scripts/data/all_response_options.csv', encoding='latin1', index_col=0)

	surveys_df = pd.read_csv('/mnt/c/Users/victo/OneDrive/Documents/Github/heroku-dashboard-4020/scripts/data/all_surveys.csv', encoding='latin1')

	all_dockets_df = pd.read_csv('/mnt/c/Users/victo/OneDrive/Documents/Github/heroku-dashboard-4020/scripts/data/all_dockets.csv', index_col=0)

	all_proceedings_df = pd.read_csv('/mnt/c/Users/victo/OneDrive/Documents/Github/heroku-dashboard-4020/scripts/data/all_proceedings.csv', index_col=0)
	'''

	'''
	# SURVEYS
	# --------
	# WORKS

	print("Beginning Surveys")
	for index, row in surveys_df.iterrows():
		fields = [int(x) if (i == 1 and len(str(x)) == 6) else 0 if (i == 1) else x if (type(x) != float) else 0 for i, x in enumerate(list(row))]
		print(fields[2])
		Survey.objects.create(survey_id=fields[0], survey_year=fields[1], survey_name=fields[2],
	 						survey_use_start_date=fields[3], survey_use_end_date=fields[4],
	 						survey_phase_id=fields[5], survey_phase_venue_type=fields[6],
	 						survey_part_id=fields[7], survey_observation_level=fields[8],
	 						observer_type=fields[9], court_id=fields[10], survey_notes=fields[11])
	print("Done Surveys {}".format('\n'*3))
	'''

	'''
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
	'''

	
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

	for index, row in responses_df.iterrows():
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
	

	

