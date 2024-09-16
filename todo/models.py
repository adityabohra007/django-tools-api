from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TodoList(models.Model):
    title = models.CharField(max_length=200, default="Title")
    created_on = models.DateTimeField(null=True)
    is_completed = models.BooleanField(null=True)
    completed_on = models.DateTimeField(null=True)
    description = models.TextField()


class Todo(models.Model):
    user = models.ForeignKey(User,default=1,on_delete = models.PROTECT)
    title = models.CharField(max_length=100, default="Title")
    created_on = models.DateTimeField(auto_now=True)
    todo_list = models.ManyToManyField(TodoList)
    category = models.CharField(max_length=200)
    custom_color_code = models.CharField(max_length=10, null=True)
    description = models.TextField()


class Customization(models.Model):
    category = models.CharField(max_length=200, default="Category")
    color = models.CharField(max_length=10, default="Color")


class CreateTest(models.Model):
    pass


class TodoLabel(models.Model):
    pass


#  quiz or test system from provided/created tests
#  Video playlist excess to show and check off the videos watched
# Hobby - label to different types so that it will make it easy to navigate to focused group
# A filter in frontend based on labels
# Creating a roadmap view.
# Then can create a roadmap questionarrie - so to keep taking the test for revision and can also add information for easy retrival
# Scheduling a test of a specific section on a specific time .
# Adding a notification of a task for specific time like - interview,meeting,class  ( this will be list subscription based system, no need for a todo to get it to work)- will also be send as email, if option is on
# Can create time session  for something.
# - can create from task it self

# Can give suggest on what hobby to go to next using AI
# Once good user base can get the sponsors
# If guitar is added to hobby right now
#  can add or update different scores to do .
# One after other can be ticked if completed .
# Can then create future test of specific date
#  Can also create random tests

# Add TextField for detail and better usage


# If this all become relevant can create plugin


# Bill split system using opencv too

# Guitar score recommendation
# Study recommendation system
# Schedule Recommandation system
