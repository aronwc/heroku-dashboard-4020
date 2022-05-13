import pandas as pd
import numpy as np
import pytz
from datetime import datetime
from django.utils.dateparse import parse_date
from website.models import Response, Question, ResponseOptions, Survey, DocketCharge, DocketProceeding

#DocketCharge.objects.all().delete()
#DocketProceeding.objects.all().delete()

all_dockets_df = pd.read_csv('./scripts/data/all_dockets.csv', index_col=0)

all_proceedings_df = pd.read_csv('./scripts/data/all_proceedings.csv')

print("Beginning DocketCharges")

for index, row in all_dockets_df.iterrows():
	fields = list(row)
	correct_date = datetime.strptime(fields[7], "%m/%d/%Y")
	tz_aware_date = pytz.timezone('US/Central').localize(correct_date) # best practice to have timezone aware dates
	DocketCharge.objects.create(mag_num=fields[0], defendant=fields[1], judge=fields[2], 
							count=fields[3], code=fields[4], charge=fields[5], bond=fields[6],
							date=tz_aware_date)
print("Done DocketCharges")
	
print("Beginning DocketProceeding")
for index, row in all_proceedings_df.iterrows():
	#print("index: ", index)
	fields = list(row)
	#print("field: ", fields[0])
	print("mag_num: ", fields[4])
	correct_date = datetime.strptime(fields[0], "%m/%d/%Y")
	tz_aware_date = pytz.timezone('US/Central').localize(correct_date)
	docket_proceeding = DocketProceeding(mag_num=index, date=tz_aware_date, 
										judge=fields[1], text=fields[2], bond_set_for=fields[3],
										mag_section=fields[4])


	docket_proceeding.save()
	docket_proceeding.docket_charges.add(*DocketCharge.objects.filter(mag_num=index))

print("Done DocketProceeding")