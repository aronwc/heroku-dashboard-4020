from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Response(models.Model):

#class Response(models.Model):



# class Response(models.Model):
#     MUNICIPAL = "MUN"
#     MAGISTRATE = "MAG"
#     CRIMINAL = "CDC"
#     COURT_CHOICES = [
#         (MUNICIPAL, "Municipal"),
#         (MAGISTRATE, "Magistrate"),
#         (CRIMINAL, "Criminal"),
#     ]
#     court = models.CharField(
#         max_length=3,
#         choices=COURT_CHOICES, 
#         default=MUNICIPAL
#         )

#     bail = models.IntegerField()

#     JUDGES_CHOICES = [
#         ("Municipal", (
#             ("Sens", "Sens"),
#             ("Jones", "Jones"),
#             ("Larche-Mason", "Larche-Mason"),
#             ("Shea", "Shea"),
#             ("Early", "Early"),
#             ("Landry", "Landry"), 
#             ("Jupiter", "Jupiter"),
#             )
#         ),
#         ("Magistrate", (
#             ("Lombard", "Lombard"),
#             ("Collins", "Collins"),
#             ("Thibodeaux", "Thibodeaux"),
#             ("Blackburn", "Blackburn"),
#             ("Friedman", "Friedman"),
#             )
#         ),
#         ("Criminal", (
#             ("White", "White"),
#             ("Davillier", "Davillier"),
#             ("Willard", "Willard"),
#             ("Holmes", "Holmes"),
#             ("Goode-Douglas", "Goode-Douglas"),
#             ("Pittman", "Pittman"),
#             ("Campbell", "Campbell"),
#             ("Buras", "Buras"),
#             ("Herman", "Herman"),
#             ("Derbigny", "Derbigny"),
#             ("DeLarge", "DeLarge"),
#             ("Harris", "Harris"),
#             )
#         ),
#         ("Don't know", "Don't know")
#     ]
#     judge = models.CharField(
#         max_length=80,
#         choices=JUDGES_CHOICES,
#         default="Sens",
#     )
    
#     ethnicity = models.CharField(max_length=80)

#     YEAR_CHOICES = [
#         ("2018", "2018"),
#         ("2019", "2019"),
#         ("2020", "2020"),
#         ("2021", "2021"),
#     ]
#     year = models.IntegerField(
#         max_length=4,
#         choices=YEAR_CHOICES, 
#         default="2021"
#     )

#     bond = models.CharField(max_length=80, default="0")
#     income = models.CharField(max_length=80, default="employed")
#     housing = models.CharField(max_length=80, default="stable")
#     representer = models.CharField(max_length=80, default="OPD")
#     ada = models.CharField(max_length=80, default="yes")
#     afford = models.CharField(max_length=80, default="yes")

<<<<<<< HEAD
#class Response_new(models.Model):
=======
class Response_new(models.Model):
>>>>>>> 97ecbda32baff759acd332f90c6be7fb76e25c5d
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


	def __str__(self):
		return self.response_option_text


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
	mag_num = models.IntegerField()
	date = models.DateTimeField('date of court session')
	judge = models.CharField(max_length=20) # real max is 10
	text = models.CharField(max_length=5000) # real max is 3695, will need to handle potential case of exceeding 5000 in future dockets
	

