from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
 	url(r'^$', 'programmer.views.main'),
	url(r'^problems$', 'programmer.views.allProblems'),
	url(r'^problems/([A-Z]+)$', 'programmer.views.problemDetail'),
	url(r'^problems/judge/([A-Z]+)$', 'programmer.views.judge'),
)