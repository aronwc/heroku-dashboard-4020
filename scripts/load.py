
'''
File to initially load data from csv's into models

'''

import pandas as pd
import numpy as np
from website.models import Response

def run():
	Response.objects.all().delete()
	response_df = pd.read_csv('/Users/bennettkahn/heroku-dashboard-4020/scripts/responses_cleaned_1.csv', index_col=0)
	for index, row in response_df.iterrows():
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



