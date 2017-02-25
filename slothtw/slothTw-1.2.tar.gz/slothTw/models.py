from django.db import models

# Create your models here.
class Course(models.Model):
	"""docstring for Course"""
	name = models.CharField(max_length=10)
	avatar = models.ImageField(default='') # 大頭貼照片
	teacher = models.CharField(max_length=10)
	school = models.CharField(max_length=10)
	book = models.CharField(max_length=50)
	syllabus = models.CharField(max_length=50)
	feedback_amount = models.PositiveIntegerField(default=0)
	feedback_freedom = models.FloatField(default=0)
	feedback_FU = models.FloatField(default=0)
	feedback_easy = models.FloatField(default=0)
	feedback_GPA = models.FloatField(default=0)
	feedback_knowledgeable = models.FloatField(default=0)

	def __str__(self):
		return self.name

class Comment(models.Model):
	course = models.ForeignKey(Course)
	raw = models.CharField(max_length=500)
	html = models.CharField(max_length=600)
	def __str__(self):
		return self.raw