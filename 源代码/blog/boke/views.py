from django.shortcuts import render
from . import models
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
	return render(request,'index.html')


def form(request):
	name = request.POST.get('name','NAME')
	connect = request.POST.get('connect','CONNECT')
	page = request.POST.get('page','PAGE')
	models.Form.objects.create(name=name,connect=connect,page=page)
	return HttpResponseRedirect(reverse('index'))




	