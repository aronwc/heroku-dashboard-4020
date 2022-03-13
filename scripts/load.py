
'''
File to initially load data from csv's into models

'''

import pandas as pd
import numpy as np
from website.models import Response, Question, ResponseOptions, Survey

def run():

	# delete all initial data
	Response.objects.all().delete()
	Question.objects.all().delete()
	ResponseOptions.objects.all().delete()
	Survey.objects.all().delete()


	responses_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/data/responses_cleaned_1.csv', encoding='latin1', index_col=0)

	questions_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/data/all.questions.csv', encoding='latin1', index_col=0)

	response_options_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/data/all.response.options.csv', encoding='latin1', index_col=0)

	surveys_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/data/all.surveys.csv', encoding='latin1')

	
	
	# transfer response csv/df to database
	# WORKS
	for index, row in responses_df.iterrows():
		print(type(list(row)[-1]))
		# we use 0 instead of np.nan because IntegerField's cannot take nans
		fields = [x if type(x) != float else 0 for x in list(row)]
		# some data validation for length of str fields
		#print(fields[3], type(fields[3]))
		#print(fields[8], type(fields[8]))
		fields[3] = str(fields[3])[:5000]
		fields[8] = str(fields[8])[:200]
		print(fields)
		#break
		Response.objects.create(survey_id=fields[0], collector_id=fields[1], response_id=fields[2],
								response_text=fields[3], question_id=fields[4],
								row_id=fields[5], choice_id=fields[6], other_id=fields[7],
								choice_text=fields[8])
	
	# transfer question csv/df to database
	# WORKS
	for index, row in questions_df.iterrows():
		fields = [x if type(x) != float else 0 for x in list(row)]
		Question.objects.create(question_id=fields[0], question_text=fields[1], question_type=fields[2], 
								question_subtype=fields[3], survey_id=fields[4])
	
	# transfer responseOption csv/df to database
	# WORKS
	for index, row in response_options_df.iterrows():
		#print(type(list(row)[3]))
		fields = [x if type(x) != float else 0 for x in list(row)]
		# unpack an iterable with '*'
		ResponseOptions.objects.create(response_option_id=fields[0], survey_id=fields[1], question_id=fields[2], 
										row_id=fields[3], row_text=fields[4], choice_id=fields[5], 
										response_option_text=fields[6])

	for index, row in surveys_df.iterrows():
		fields = [x if type(x) != float else 0 for x in list(row)]
		Survey.objects.create(survey_id=fields[0], survey_year=fields[1], survey_name=fields[2],
							survey_use_start_date=fields[3], survey_use_end_date=fields[4],
							survey_phase_id=fields[5], survey_phase_venue_type=fields[6],
							survey_part_id=fields[7], survey_observation_level=fields[8],
							observer_type=fields[9], court_id=fields[10], survey_notes=fields[11])




