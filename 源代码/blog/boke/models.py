from __future__ import unicode_literals
from django.db import models



class Form(models.Model):
	name= models.CharField(max_length=32,default='name')
	connect= models.CharField(max_length=64,default='connect')
	page=models.TextField(null=True)