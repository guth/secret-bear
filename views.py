import os
import IdeoneHelper
import logging

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
	for ext in templates:
		fileName = os.path.join(os.path.dirname(__file__), problemPath, 'templates/template.%s')
		fileName = fileName % ext
		f = open(fileName, 'r')
		
		sourceCode = f.read()
		sourceDict[ext] = sourceCode

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

def judge(request, name):
	language = request.POST.get('language')
	sourceCode = request.POST.get('editor')
	log.debug("Language: %s" % language)
	log.debug("Source length: %d" % len(sourceCode))

	inputFileName = os.path.join(os.path.dirname(__file__), 'problems/%s/input')
	inputFileName = inputFileName % name
	inputString = open(inputFileName, 'r').read()
	log.debug("Input length: %d" % len(inputString))
	
	outputFileName = os.path.join(os.path.dirname(__file__), 'problems/%s/output')
	outputFileName = outputFileName % name
	outputString = open(outputFileName, 'r').read()
	log.debug("Ouput length: %d" % len(outputString))
	
	result = IdeoneHelper.submitAndReturnOutput(sourceCode, language, inputString)
	log.debug("Result: %s" % result)

	try:
		if result <= 20:
			errorString = IdeoneHelper.errorStrings[result]
			log.debug("Error string: %s" % errorString)
			return HttpResponse(errorString)
		else:
			int('abc')
	except:
		log.debug("Comparing strings...")
		if str(result).strip() == str(outputString).strip():
			log.debug("AC!")
			return HttpResponse("Answer Correct")
		else:
			log.debug("WA!")
			return HttpResponse("Wrong Answer")

	return HttpResponse("Foo")