import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

log = logging.getLogger(__name__)

def validUsername(username):
	""" Checks if the given string is a valid username. Usernames
	consist only of letters, numbers, and underscores. """
	for c in username:
		if not c.isalpha() and not c.isdigit() and c != '_':
			return False
	return True

def validPassword(password):
	""" Checks if the given string is a valid password. Passwords
	cannot have spaces in them. """
	return not (' ' in password)


@require_http_methods(['GET'])
def logout_view(request):
	logout(request)
	return redirect(reverse('mainView'))

@require_http_methods(['GET', 'POST'])
def login_view(request):
	if request.method == 'GET':
		return redirect(reverse('mainView'))
	else: # POST
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect(reverse('mainView'))
		else:
			messages.error(request, 'Login failed.')
			return redirect(reverse('mainView'))

@require_http_methods(['GET', 'POST'])
def signup_view(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return redirect(reverse('mainView'))
		else:
			return render(request, 'signup.html')
	else: # POST
		username = request.POST.get('username')
		password = request.POST.get('password')
		verifyPassword = request.POST.get('verifyPassword')
		email = request.POST.get('email')
		formSuccess = True

		# Validate username input
		if not username or not validUsername(username):
			messages.error(request, "Username was not valid.")
			formSuccess = False

		# Validate password input
		if not password or not verifyPassword:
			messages.error(request, "Please enter a password twice.")
			formSuccess = False
		elif password and verifyPassword and password != verifyPassword:
			messages.error(request, "Passwords much match.")
			formSuccess = False
		elif not validPassword(password):
			messages.error(request, "Passwords cannot contain spaces.")
			formSuccess = False

		if not formSuccess:
			return redirect(reverse('signupView'))

		try:
			user = User.objects.get(username=username)
			messages.error(request, "The username you entered is already taken.")
			return redirect(reverse('signupView'))
		except:
			# User doesn't exist, create the user and login.
			User.objects.create_user(username=username, password=password, email=email)
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect(reverse('mainView'))