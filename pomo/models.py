from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
from  django.db.models   import Q
from django.utils import timezone
# Create your models here.
class Paused(models.Model):
    '''This is used to manage pause data 
    If a timer is paused before ends 
    '''
    start_time = models.DateTimeField()
    end_time =models.DateTimeField(null=True)
    is_active= models.BooleanField(default=True)
    
class TimerQuerySet(models.QuerySet):
    def completed(self):
        return self.filter(Q(is_completed=True)|Q(end_time__lt=timezone.now()))
class Timer(models.Model):
    '''Calculate from start_time to current time , then countdown to 0'''
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)# at the at which   , when pause is added each time its value changes , like if pause starts then 
    #nothing changes but when pause ends update endtime accordig to pauses between the start_time and end_time and time taken by pauses to total to 25min for now
    is_completed =models.BooleanField(default=False) # when completed is pressed is false
    completion_time = models.DateTimeField(null=True)
    is_paused = models.BooleanField(default=False) # when paused , to start create new instance of timer where it complete remaining time
    paused = models.ManyToManyField(Paused,null=True,blank=True) # save all pause data here  so as to calculate the completetion of timer based on pause
    user =models.ForeignKey(User,on_delete=models.PROTECT)
    total_time = models.IntegerField(default=25)
    custom = TimerQuerySet.as_manager()
    objects = models.Manager()
    def __str__(self):
        return str(self.start_time)+'----'+str(self.end_time)+"---"+str(self.is_completed)
class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)
class Task(models.Model):
    '''Right now without auth'''
    title = models.CharField(max_length=100)
    description = models.CharField(null=True,blank=True,max_length=500)
    want_to_focus = models.IntegerField()
    check_off = models.BooleanField(default=False,null=True) # just for indication that it is completed nothing much
    is_deleted= models.BooleanField(default=False,null=True) # no instance is every deleted they are hidden from current instances
    # is_selected = models.BooleanField(default=False,null=True)
    user= models.ForeignKey(User,on_delete=models.PROTECT)
    task = TaskQuerySet.as_manager()
    objects= models.Manager()

class TaskSelected(models.Model):
    '''Any task that is in this model is the selected task'''
    task = models.OneToOneField(Task,on_delete=models.PROTECT)
    # selected = models.BooleanField(default=False)
    user = models.OneToOneField(User,on_delete=models.PROTECT,default=1)
    
class TaskPosition(models.Model):
    position = models.IntegerField(null=True)
    task = models.OneToOneField(Task,on_delete=models.CASCADE)
    
    
class TaskTimer(models.Model):
    timer = models.ForeignKey(Timer,on_delete=models.CASCADE)
    task = models.ForeignKey(Task,on_delete=models.CASCADE)


class Theme(models.Model):
    short_break = models.CharField(max_length=10)
    long_break =  models.CharField(max_length=10)
    pomodoro =  models.CharField(max_length=10)
    # user = models.OneToOneField(User,on_delete=models.PROTECT,default=1)

class Configuration(models.Model):
    theme = models.OneToOneField(Theme,on_delete=models.PROTECT)
    pomo_time = models.IntegerField()
    short_break_time = models.IntegerField()
    long_break_time = models.IntegerField()
    user = models.OneToOneField(User,on_delete=models.PROTECT,default=1)
    
# class CustomPomoCount(models.Model):
#     '''To store custom added pomo completed time
#         which will not be included in chart
#     '''
#     task = models.ForeignKey(Task)
#     start_time = models.DateTimeField()
#     count = models.IntegerField()

class Break(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    break_type = models.CharField(choices=(('LONG','LONG'),('SHORT','SHORT')),max_length=5)
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    def __str__(self):
        return self.break_type +'('+str(self.start_time)+'-'+str(self.end_time)+')'
    
# class TaskTemplateItem(Task):
#     # testing = models.CharField(max_length=100)
#     class Meta:
#         db_table = 'TaskTemplateItem'
#         # managed = True
#         # verbose_name = 'ModelName'
#         # verbose_name_plural = 'ModelNames'
class TaskTemplateItem(models.Model):
    '''Right now without auth'''
    title = models.CharField(max_length=100)
    description = models.CharField(null=True,blank=True,max_length=500)
    want_to_focus = models.IntegerField()
    check_off = models.BooleanField(default=False,null=True)
    is_deleted= models.BooleanField(default=False,null=True)
    # is_selected = models.BooleanField(default=False,null=True)
    user= models.ForeignKey(User,on_delete=models.PROTECT)
class TaskTemplate(models.Model):
    name = models.CharField(max_length=100)
    task = models.ManyToManyField(TaskTemplateItem)
    user = models.ForeignKey(User,on_delete=models.PROTECT,default=1)
