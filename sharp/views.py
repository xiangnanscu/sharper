from django.shortcuts import render
#from django.template.response import TemplateResponse
from djjinja2.response import TemplateResponse
from django.views.generic.base import TemplateView

def home(request):
	user = request.user
	if 'visits' not in request.session:
		request.session['visits']=0
	request.session['visits']+=1
	return TemplateResponse(request, 'home.html', locals(),)
def test(request):
	#print(request.path)
	return TemplateResponse(request, 'b.html', locals(),)
