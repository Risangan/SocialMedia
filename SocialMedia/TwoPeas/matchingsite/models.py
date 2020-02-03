from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Hobby(models.Model):
	
	hobbyName = models.CharField(max_length=250)

	def __str__(self):
		return self.hobbyName

class Profile(User):
	GENDER_OPTIONS = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
	profileImage = models.ImageField(upload_to='profile_images')
	gender = models.CharField(max_length=1, choices=GENDER_OPTIONS)
	dateOfBirth = models.DateField(max_length=8)
	hobbies = models.ManyToManyField(Hobby)
	likes = models.ManyToManyField(
        to='self',
        blank=True,
        symmetrical=True
    )

	def __str__(self):
		return self.username