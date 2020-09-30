from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User, auth
from multiselectfield import MultiSelectField

genres_choices = [("1", "Action"),
                  ("2","Adventure"),
                  ("3", "Animation"),
                  ("4", "Children's"),
                  ("5", "Comedy"),
                  ("6","Crime"),
                  ("7","Drama"),
                  ("8","Fantasy"),
                  ("9","Film - Noir "),
                  ("10","Horror"),
                  ("11","Musical"),
                  ("12","Mystery"),
                  ("13","Romance"),
                  ("14","Sci - Fi"),
                  ("15", "Thriller"),
                  ("16","War"),
                  ("17","Western")]

class LoginSignup(models.Model):

    UserName = models.CharField(max_length=100)
    Password = models.CharField(max_length=100)
    email   = models.EmailField(max_length=100)
    Age = models.IntegerField()
    Sex = models.CharField(max_length=100)
    Profession = models.CharField(max_length=100)

    def __str__(self):
        return self.UserName

class Myrating(models.Model):

    user  	= models.ForeignKey(User , on_delete=models.CASCADE)
    movie_id 	= models.IntegerField()
    rating 	= models.IntegerField(default=0,validators=[MaxValueValidator(5),MinValueValidator(0)])


