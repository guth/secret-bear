import judge
import languages
import logging
import os
import status

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from models import Problem

log = logging.getLogger(__name__)

def main(request):
	return render(request, 'main.html')

def account(request):
	return render(request, 'account.html')

def allProblems(request):
	problems = Problem.objects.all()
	count = len(problems)
	return render(request, 'problems.html', {'problems':problems, 'count':count})

templates = ['java', 'py']
def problemDetail(request, name):
	problem = Problem.objects.get(name=name)
	if not problem:
		return "Problem %s doesn't exist." % name
	
	problemPath = 'problems/%s/' % name

	sourceDict = {}
	sourceDict[languages.JAVA_EXT] = problem.javaTemplate
	sourceDict[languages.PYTHON_EXT] = problem.pythonTemplate

	foldsDict = {}
	f = open(os.path.join('programmer/' + problemPath + 'folds.info'), 'r')
	foldsInfo = f.read()
	f.close()
	for line in foldsInfo.split("\n"):
		parts = line.split(" ")
		lang = parts[0]
		foldsDict[lang] = [int(parts[i]) for i in range(1,len(parts))]
	
	return render(request, "problem.html", {'problem':problem, 'sourceDict':sourceDict,
											'foldsDict':foldsDict})

def judgeProblem(request, name):
	if not request.user.is_authenticated():
		return HttpResponse("Please log in to submit your solution")

	language = request.POST.get('language')
	sourceCode = request.POST.get('editor')
	problem = Problem.objects.get(name=name)

	inputString = problem.standardInput
	outputString = problem.expectedOutput.replace('\r', '')
	
	result = judge.executeProgram(sourceCode, language, inputString, outputString)
	resultText = status.resultCodeToText(result)

	if resultText:
		return HttpResponse(resultText)
	else:
		return HttpResponse("Invalid response. Something went wrong!")