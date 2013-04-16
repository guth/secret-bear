import judge
import languages
import logging
import os
import status

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from models import Problem, Submission

log = logging.getLogger(__name__)

def main(request):
	return render(request, 'main.html')

def account(request):
	if not request.user.is_authenticated():
		return render(request, 'main.html')
	
	acSubmissions = Submission.objects.filter(user=request.user, result='AC')
	acSubmissions = acSubmissions.values('problem').distinct()
	numSolves = acSubmissions.count()

	return render(request, 'account.html', {'acSubmissions':acSubmissions,
											'numSolves':numSolves})

def submissions(request):
	if not request.user.is_authenticated():
		return render(request, 'main.html')

	submissions = Submission.objects.filter(user=request.user).order_by('-submissionDate')
	return render(request, 'submissions.html', {'submissions':submissions})

def allProblems(request):
	problems = Problem.objects.all().order_by('-publishedDate')
	count = problems.count()
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

	# If a submission ID was passed, put that code as the template.
	sid = request.GET.get('sid')
	if sid:
		submission = Submission.objects.get(id=sid)
		ext = languages.langToExt[submission.language]
		sourceDict[ext] = submission.sourceCode
	
	return render(request, "problem.html", {'problem':problem, 'sourceDict':sourceDict})

def judgeProblem(request, name):
	if not request.user.is_authenticated():
		return HttpResponse("Please log in to submit your solution.")

	language = request.POST.get('language')
	sourceCode = request.POST.get('editor')
	problem = Problem.objects.get(name=name)

	inputString = problem.standardInput
	outputString = problem.expectedOutput.replace('\r', '')
	
	result = judge.subprocessJudge(sourceCode, language, inputString, outputString)
	resultTuple = status.resultCodeToText(result)
	
	if resultTuple:
		s = Submission(user=request.user, problem=problem, result=resultTuple[0],
			sourceCode=sourceCode, language=language)
		s.save()
		resultText = resultTuple[1]
		return HttpResponse(resultText)
	else:
		return HttpResponse("Invalid response. Something went wrong!")