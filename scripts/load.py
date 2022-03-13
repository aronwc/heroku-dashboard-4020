
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


	responses_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/responses_cleaned_1.csv', index_col=0)

	questions_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/all.questions.csv', index_col=0)

	response_options_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/all.response.options.csv', index_col=0)

	surveys_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/all.surveys.csv')



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



