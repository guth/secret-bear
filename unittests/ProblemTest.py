import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from programmer.models import Problem, Submission

class ProblemTest(TestCase):
	def setUp(self):
		self.p1 = Problem.objects.create(name="TEST1", description="Test description",
			problemStatement="Test a problem and you win.", publishedDate=timezone.now())
		self.p2 = Problem.objects.create(name="TEST2", description="Test description 2",
			problemStatement="Test a problem twice and you win.",
			publishedDate=timezone.now() + datetime.timedelta(days=1))
		self.p3 = Problem.objects.create(name="TEST3", description="Test description 3",
			problemStatement="Test a problem three times and you win.",
			publishedDate=timezone.now() + datetime.timedelta(days=2))

		self.user = User.objects.create_user(username="foo", password="password")
		Submission.objects.create(user=self.user, problem=self.p1, result="RTE")
		Submission.objects.create(user=self.user, problem=self.p1, result="WA")
		Submission.objects.create(user=self.user, problem=self.p1, result="AC")
		Submission.objects.create(user=self.user, problem=self.p2, result="AC")
		Submission.objects.create(user=self.user, problem=self.p2, result="WA")
		Submission.objects.create(user=self.user, problem=self.p3, result="RTE")
		Submission.objects.create(user=self.user, problem=self.p3, result="CE")
		Submission.objects.create(user=self.user, problem=self.p3, result="TLE")
		Submission.objects.create(user=self.user, problem=self.p3, result="WA")

	def test_problems_unique(self):
		self.assertNotEqual(self.p1.name, self.p2.name)

		with self.assertRaises(IntegrityError):
			p4 = Problem.objects.create(name="TEST2", description="", problemStatement="",
				publishedDate=timezone.now())
	
	def test_published_order(self):
		self.assertTrue(self.p1.publishedDate < self.p2.publishedDate)

	def test_getSolvedProblems(self):
		solved = Problem.getSolvedProblems(self.user)
		self.assertTrue(self.p1.name in solved)
		self.assertTrue(self.p2.name in solved)
		self.assertTrue(self.p3.name not in solved)

		tempUser = User.objects.create_user(username="bar", password="password")
		solved = Problem.getSolvedProblems(tempUser)
		self.assertEqual(len(solved), 0)
