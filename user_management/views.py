#from django.shortcuts import render
from django.views.generic.base import TemplateView

class Login(TemplateView):
    template_name = "user_management/login.html"
