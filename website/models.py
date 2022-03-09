from django.db import models

# Create your models here.

class Responses(models.Model):
    MUNICIPAL = "MUN"
    MAGISTRATE = "MAG"
    CRIMINAL = "CDC"
    COURT_CHOICES = [
        (MUNICIPAL, "Municipal"),
        (MAGISTRATE, "Magistrate"),
        (CRIMINAL, "Criminal"),
    ]
    court = models.CharField(
        max_length=3,
        choices=COURT_CHOICES, 
        default=MUNICIPAL
        )

    bail = models.IntegerField()

    JUDGES_CHOICES = [
        ("Municipal", (
            ("Sens", "Sens"),
            ("Jones", "Jones"),
            ("Larche-Mason", "Larche-Mason"),
            ("Shea", "Shea"),
            ("Early", "Early"),
            ("Landry", "Landry"), 
            ("Jupiter", "Jupiter"),
            )
        ),
        ("Magistrate", (
            ("Lombard", "Lombard"),
            ("Collins", "Collins"),
            ("Thibodeaux", "Thibodeaux"),
            ("Blackburn", "Blackburn"),
            ("Friedman", "Friedman"),
            )
        ),
        ("Criminal", (
            ("White", "White"),
            ("Davillier", "Davillier"),
            ("Willard", "Willard"),
            ("Holmes", "Holmes"),
            ("Goode-Douglas", "Goode-Douglas"),
            ("Pittman", "Pittman"),
            ("Campbell", "Campbell"),
            ("Buras", "Buras"),
            ("Herman", "Herman"),
            ("Derbigny", "Derbigny"),
            ("DeLarge", "DeLarge"),
            ("Harris", "Harris"),
            )
        ),
        ("Don't know", "Don't know")
    ]
    judge = models.CharField(
        max_length=80,
        choices=JUDGES_CHOICES,
        default="Sens",
    )
    
    ethnicity = models.CharField(max_length=80)

    YEAR_CHOICES = [
        ("2018", "2018"),
        ("2019", "2019"),
        ("2020", "2020"),
        ("2021", "2021"),
    ]
    year = models.IntegerField(
        max_length=4,
        choices=YEAR_CHOICES, 
        default="2021"
    )