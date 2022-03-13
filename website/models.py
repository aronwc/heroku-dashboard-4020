from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class Response(models.Model):
	survey_id = models.BigIntegerField()
	collector_id = models.BigIntegerField()
	response_id = models.BigIntegerField()
	response_text = models.CharField(max_length=5000) # longest in given response_cleaned csv was 4576
	question_id = models.BigIntegerField()
	row_id = models.BigIntegerField(default=0)
	choice_id = models.BigIntegerField()
	other_id = models.BigIntegerField()
	choice_text = models.CharField(max_length=200) # max is 195 in given data
	def __str__(self):
		return self.response_text


class Question(models.Model):
	question_id = models.BigIntegerField()
	question_text = models.CharField(max_length=600)
	question_type = models.CharField(max_length=30)
	question_subtype = models.CharField(max_length=30)
	survey_id = models.BigIntegerField()
	def __str__(self):
		return self.question_text


class ResponseOptions(models.Model):
	response_option_id = models.CharField(max_length=40)
	survey_id = models.BigIntegerField()
	question_id = models.BigIntegerField()
	row_id = models.BigIntegerField()
	row_text = models.CharField(max_length=300)
	choice_id = models.BigIntegerField()
	response_option_text = models.CharField(max_length=500)

