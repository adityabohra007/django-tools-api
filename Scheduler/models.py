from django.db import models

# Create your models here.


class Category(models.Model):
    title = models.CharField()
    color_code = models.CharField()
    text_color = models.CharField()


class Schedule(models.Model):
    title = models.CharField()
    date_created = models.DateTimeField()
    tasks = models.ManyToManyField("")
    category = models.ForeignKey(Category,on_delete=models.SET_NULL)
