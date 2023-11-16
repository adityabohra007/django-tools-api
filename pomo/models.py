from collections.abc import Iterable
from django.db import models

# Create your models here.
class Paused(models.Model):
    '''This is used to manage pause data 
    If a timer is paused before ends 
    '''
    start_time = models.DateTimeField()
    end_time =models.DateTimeField(null=True)
    is_active= models.BooleanField(default=True)
    
class Timer(models.Model):
    '''Calculate from start_time to current time , then countdown to 0'''
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)# at the at which   , when pause is added each time its value changes , like if pause starts then 
    #nothing changes but when pause ends update endtime accordig to pauses between the start_time and end_time and time taken by pauses to total to 25min for now
    is_completed =models.BooleanField(default=True) # when completed is pressed is false
    completion_time = models.DateTimeField(null=True)
    is_paused = models.BooleanField(default=False) # when paused , to start create new instance of timer where it complete remaining time
    paused = models.ManyToManyField(Paused,null=True,blank=True) # save all pause data here  so as to calculate the completetion of timer based on pause

    
class Task(models.Model):
    '''Right now without auth'''
    title = models.CharField(max_length=100)
    description = models.TextField()
    want_to_focus = models.IntegerField()
    check_off = models.BooleanField(default=False,null=True)
    is_deleted= models.BooleanField(default=False,null=True)

class TaskSelected(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    selected = models.BooleanField(default=False)
    
class TaskPosition(models.Model):
    position = models.IntegerField(null=True)
    task = models.OneToOneField(Task,on_delete=models.CASCADE)
    
    
class TaskTimer(models.Model):
    timer = models.ForeignKey(Timer,on_delete=models.CASCADE)
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    