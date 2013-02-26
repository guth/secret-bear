from django.conf.urls import patterns, include, url

urlpatterns = patterns('programmer.views',
 	url(r'^$', 'main', name='mainView'),
	url(r'^problems$', 'allProblems', name='allProblemsView'),
	url(r'^problems/([A-Z]+)$', 'problemDetail', name='problemDetailView'),
	url(r'^problems/judge/([A-Z]+)$', 'judge', name='judgeView'),
)

urlpatterns += patterns('programmer.auth',
	url(r'^logout$', 'logout_view', name='logoutView'),
	url(r'^login$', 'login_view', name='loginView'),
	url(r'^signup$', 'signup_view', name='signupView'),
)