from django.db import models

class Problem(models.Model):
	name = models.CharField(max_length=10)
	description = models.TextField()
	problemStatement = models.TextField()
	publishedDate = models.DateTimeField()

	def __unicode__(self):
		return self.name