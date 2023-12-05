from django.test import TestCase
from .models import Timer,Task,TaskTimer
from rest_framework.test import APIRequestFactory # for bypassing middleware and other thing
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient # for real request
# Create your tests here.
from django.test import Client
# class TimerTest(TestCase):
#     def setUp(self):
#         Timer.objects.create()

class TimerAllStateTestCase(TestCase):
    def setUp(self):
        self.factory = APIClient()
        # print(task_request.body)
    def test_post_request(self):
        task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
        # print(task_request.body)
        request = self.factory.post('/pomo/timer/start',{'start_time':timezone.now(),'task':1})
        print(request,Task.objects.all())
        print(Timer.objects.all())
        timer = Timer.objects.get(id=1)
        self.assertEqual(timer.id,1)
        pause_request = self.factory.post('/pomo/timer/update',{'state':'pause','current_time':timezone.now()+timedelta(minutes=10),'timer':1})
        timer_paused = Timer.objects.get(id=1)
        self.assertEqual(timer_paused.is_paused,True)
        print(timer_paused.paused.all())
        self.assertEqual(len(timer_paused.paused.all()),1)
        end_time_check = timer_paused.paused.first()
        self.assertEqual(end_time_check.end_time,None)
        # Now unpausing
        unpausing = self.factory.post('/pomo/timer/update',{'state':'unpause','end_time':timezone.now()+timedelta(minutes=15),'timer':1})
        check_timer = Timer.objects.get(id=1)
        final = timezone.now()+timedelta(minutes=30)
        self.assertEqual(check_timer.end_time.hour,final.hour)
        self.assertEqual(check_timer.end_time.min,final.min)
        self.assertEqual(check_timer.end_time.second,final.second)
        # Second time pausing
        pause_request = self.factory.post('/pomo/timer/update',{'state':'pause','current_time':timezone.now()+timedelta(minutes=2),'timer':1})
        timer_paused = Timer.objects.get(id=1)
        self.assertEqual(timer_paused.is_paused,True)
        print(timer_paused.paused.all())
        self.assertEqual(len(timer_paused.paused.all()),2)
        end_time_check = timer_paused.paused.first()
        self.assertEqual(end_time_check.end_time,None)
        # # Is there any duplicate timer allowed or not 
        # check_if_duplicate_timer = self.factory.post('/pomo/timer/start',{'start_time':timezone.now(),'task':1})
        # self.assertEqual(check_if_duplicate_timer.status_code,403)
        # # completion 
        # completion = self.factory.post('/pomo/timer/update',{'state':'completed','completion_time':timezone.now(),'timer':1})
        # self.assertEqual(completion.status_code,200)
        # # once completion is completed checking status of timer ,as in is timer on ?
        # status = self.factory.get('/pomo/timer/status',{'timer':1})
        # self.assertEqual(status.status_code,200)
        # self.assertEqual(status.data['status'],'completed')
        # #now since it is completed then we can create a new timer
        # new_timer =  self.factory.post('/pomo/timer/start',{'start_time':timezone.now(),'task':1})
        # timer = Timer.objects.filter()
        # self.assertEqual(timer.count(),2)
        
        # # now just give me the time left in clock for my task
        # status = self.factory.get('/pomo/timer/status',{'timer':2})
        # self.assertEqual(int(str(status.data['time_left']).split(':')[1]),25)
        
        # # now check how many pomo completed today for a task
        # task = Task.objects.get(id=1)
        # task_timer = TaskTimer.objects.filter(task=task,timer__is_completed=True,timer__end_time__lt=timezone.now()+timedelta(minutes=26))# this is for all time
        
        # task_timer_today = TaskTimer.objects.filter(task=task,timer__is_completed=True,timer__end_time__lt=timezone.now(),timer__start_time__date__gt=timezone.now())# this is for today time

        # print(task_timer)
        
        
        # then work on how many tasks completed today
        
class TaskTestCase(TestCase):
    def setUp(self):
        self.factory = APIClient()
    
    def test_task_create_update(self):
        task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
        self.assertEqual(task_request.status_code,201)
        # Get for ListTaskView
        task_list = self.factory.get('/pomo/task/list',format='json')
        self.assertEqual(task_list.status_code,200)
        self.assertEqual(len(task_list.data),1)
        # Updating task data
        task_request = self.factory.put('/pomo/task',{'task':1,'title':'X',},format='json')
        self.assertEqual(task_request.status_code,202)
        self.assertEqual(Task.objects.get(id=1).title,'X')
        # Updating want_to_focus
        task_request = self.factory.put('/pomo/task',{'task':1,'want_to_focus':4,},format='json')
        self.assertEqual(task_request.status_code,202)
        self.assertEqual(Task.objects.get(id=1).want_to_focus,4)
        task_request = self.factory.put('/pomo/task',{'task':1,'want_to_focus':1,},format='json')
        self.assertEqual(task_request.status_code,202)
        self.assertEqual(Task.objects.get(id=1).want_to_focus,1)
        
        # Deleting a task  : It wont delete a task since we want to show the history therefore we will add is_deleted to just show that task is not in list
        # but also need to add a method to wipe the task off the system
        