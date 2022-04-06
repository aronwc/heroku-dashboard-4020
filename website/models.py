from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Survey(models.Model):
	survey_id = models.BigIntegerField()
	survey_year = models.IntegerField()
	survey_name = models.CharField(max_length=100)
	survey_use_start_date = models.IntegerField()
	survey_use_end_date = models.IntegerField()
	survey_phase_id = models.IntegerField()
	survey_phase_venue_type = models.CharField(max_length=15)
	survey_part_id = models.CharField(max_length=10)
	survey_observation_level = models.CharField(max_length=15)
	observer_type = models.CharField(max_length=40)
	court_id = models.CharField(max_length=20)
	survey_notes = models.CharField(max_length=40)

	def __str__(self):
		return str(self.court_id) + ', Survey ID: ' + str(self.survey_id)

class Question(models.Model):
	question_id = models.BigIntegerField()
	question_text = models.CharField(max_length=600)
	question_type = models.CharField(max_length=30)
	question_subtype = models.CharField(max_length=30)
	survey = models.ForeignKey(Survey, on_delete=models.CASCADE, default=0) # Survey to Question = One to Many
	cluster_id = models.IntegerField(default=-1)
	def __str__(self):
		return str(self.question_text)


class Response(models.Model):

	# In Question, we can think of question_id as primary key because it is unique
	# in given csv (responses_cleaned), there is no unique key, so primary key is IT

	responder_id = models.BigIntegerField() # remember that all answers of one RESPONDER (person) to a survey has same 'response_id' in SM API (we rename it responder_id here)
	survey = models.ForeignKey(Survey, on_delete=models.CASCADE, default=0) # Survey to Response = One to Many
	collector_id = models.BigIntegerField()
	response_text = models.CharField(max_length=5000) # longest in given response_cleaned csv was 4576
	row_id = models.BigIntegerField(default=0)
	choice_id = models.BigIntegerField()
	other_id = models.BigIntegerField()
	choice_text = models.CharField(max_length=200) # max is 195 in given data
	question = models.ForeignKey(Question, on_delete=models.CASCADE, default=0) # One Question has many Response(s) and one Response has many Question(s)
	def __str__(self):
		return str(self.response_text)



class ResponseOptions(models.Model):
	response_option_id = models.CharField(max_length=40)
	survey_id = models.BigIntegerField()
	row_id = models.BigIntegerField()
	row_text = models.CharField(max_length=300)
	choice_id = models.BigIntegerField()
	response_option_text = models.CharField(max_length=500)
	question = models.ForeignKey(Question, on_delete=models.CASCADE, default=0) # Question to ResponseOptions = One to Many


	def __str__(self):
		return str(self.response_option_text)


class DocketCharge(models.Model):
	mag_num = models.IntegerField()
	defendant = models.CharField(max_length=50) # real max is 32
	judge = models.CharField(max_length=20) # real max is 10
	count = models.IntegerField()
	code = models.CharField(max_length=40) # real max is 24
	charge = models.CharField(max_length=200) # real max is 130
	bond = models.IntegerField()
	date = models.DateTimeField('date of court session') # 'date of court session' is the machine-readable name of field


class DocketProceeding(models.Model):
	mag_num = models.IntegerField() # One DocketCharge has many Proceedings, while one Proceeding has one DocketCharge
	date = models.DateTimeField('date of court session')
	judge = models.CharField(max_length=20) # real max is 10
	text = models.CharField(max_length=5000) # real max is 3695, will need to handle potential case of exceeding 5000 in future dockets
	bond_set_for = models.FloatField(blank=True, null=True) 
	docket_charges = models.ManyToManyField(DocketCharge)

