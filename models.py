from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
	name = models.CharField(max_length=10, primary_key=True)
	description = models.TextField()
	problemStatement = models.TextField()
	publishedDate = models.DateTimeField()

	javaTemplate = models.TextField()
	pythonTemplate = models.TextField()

	standardInput = models.TextField()
	expectedOutput = models.TextField()

	@staticmethod
	def getSolvedProblems(user):
		""" Returns a set of all problem names solved by the user. """
		solved = Submission.objects.filter(user=user, result='AC')
		solved = solved.values('problem').distinct()
		solved = {s['problem'] for s in solved}
		return solved

	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		return '/prog/problems/%s' % self.name

class Submission(models.Model):
	RESULT_CHOICES = (
		('AC', 'Answer Correct'),
		('WA', 'Wrong Answer'),
		('CE', 'Compilation Error'),
		('RE', 'Runtime Error'),
		('TLE', 'Time Limit Exceeded'),
	)
	user = models.ForeignKey(User)
	problem = models.ForeignKey(Problem)
	result = models.CharField(max_length=3, choices=RESULT_CHOICES)
	
	sourceCode = models.TextField()
	language = models.CharField(max_length=20)

	submissionDate = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return '<%s, %s, %s, %s, %s>' % (self.user.username,
			self.problem.name, self.result, self.language,
			self.submissionDate.strftime("%D %T"))