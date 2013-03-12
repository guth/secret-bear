import datetime
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from programmer.models import Problem

class ProblemTest(TestCase):
    def setUp(self):
        self.p1 = Problem.objects.create(name="TEST1", description="Test description",
        	problemStatement="Test a problem and you win.", publishedDate=timezone.now())
        self.p2 = Problem.objects.create(name="TEST2", description="Test description",
        	problemStatement="Test a problem and you win.",
        	publishedDate=timezone.now() + datetime.timedelta(days=1))

    def test_problems_unique(self):
    	self.assertNotEqual(self.p1.name, self.p2.name)

    	with self.assertRaises(IntegrityError):
    		p3 = Problem.objects.create(name="TEST2", description="", problemStatement="",
    			publishedDate=timezone.now())
    
    def test_published_order(self):
    	self.assertTrue(self.p1.publishedDate < self.p2.publishedDate)