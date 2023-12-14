from django.test import TestCase
from ..models import Timer,Task,TaskTimer,Configuration,Theme,Paused
from rest_framework.test import APIRequestFactory # for bypassing middleware and other thing
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient # for real request
from ..utils import time_left_in_seconds
import time
# Create your tests here.
from django.test import Client
from ..serializers import TaskSerializer,ConfigurationSerializer,ThemeSerializer,ConfigurationFormSerializer
from django.contrib.auth.models import User
# class TimerTest(TestCase):
#     def setUp(self):
#         Timer.objects.create()

class TimerAllStateTestCase(TestCase):
    def setUp(self):
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()

        # print(task_request.body)
    def test_post_request(self):
        # One task
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        self.factory.credentials(AUTHORIZATION='Bearer '+login.data['access'])
        # self.factory.force_authenticate(user=user)
        task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
        # print(task_request.body)
        # Starting timer
        
        print(task_request.status_code,'one')
        task_one = Task.objects.first()
        self.assertEqual(task_one.title,'Pomo project')
        print(timezone.now(),'starting timers----')
        
        request = self.factory.post('/pomo/timer/start',{'start_time':timezone.now(),'task':1})
        timer = Timer.objects.get(id=1)
        self.assertEqual(timer.id,1)
        time.sleep(1) # timer running
        # Pausing
        print('Pausing--`')
        pause_request = self.factory.post('/pomo/timer/update',{'state':'pause','current_time':timezone.now()+timedelta(minutes=10),'timer':1})
        timer_paused = Timer.objects.get(id=1)
        self.assertEqual(timer_paused.is_paused,True)# is_paused
        self.assertEqual(len(timer_paused.paused.all()),1)
        self.assertEqual(timer_paused.paused.first().end_time,None)
        end_time_check = timer_paused.paused.first()
        self.assertEqual(end_time_check.end_time,None)
        
        # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        status_request = self.factory.get('/pomo/timer/status')
        # calculating end_time when paused
        status_timer= Timer.objects.first()
        output= status_request.data['end_time']
        expected =timezone.now()+timedelta(minutes=time_left_in_seconds(status_timer)/60)
        self.assertEqual(output.date(),expected.date())
        self.assertEqual(output.month,expected.month)
        self.assertEqual(output.hour,expected.hour)
        self.assertAlmostEquals(output.minute,expected.minute)
        self.assertEqual(output.second,expected.second)



        # # Now unpausing
        print('Unpausing--')
        unpausing = self.factory.post('/pomo/timer/update',{'state':'unpause','timer':1})
        check_timer = Timer.objects.get(id=1)
        final = timezone.now()+timedelta(minutes=30)
        # self.assertEqual(check_timer.end_time.hour,final.hour)
        # self.assertEqual(check_timer.end_time.min,final.min)
        # Timer Status Checking 

        time.sleep(2)#timer running total to 3
        status_request = self.factory.get('/pomo/timer/status')

        output= status_request.data['end_time']
        # print(output,'output')
        # print(time_left_in_seconds(check_timer)/60,timedelta(minutes=time_left_in_seconds(check_timer)/60))
        # self.assertEqual(output.date(),final_end_time.date())
        expected =timezone.now()+timedelta(minutes=time_left_in_seconds(check_timer)/60)
        # print(expected,'expected')
        self.assertEqual(output.month,expected.month)
        self.assertEqual(output.hour,expected.hour)
        self.assertEqual(output.minute,expected.minute)
        self.assertEqual(output.second,expected.second)
        
        # # Second time pausing
        pause_request = self.factory.post('/pomo/timer/update',{'state':'pause','current_time':timezone.now()+timedelta(minutes=2),'timer':1})
        timer_paused = Timer.objects.get(id=1)
        
        
        # output= pause_request.data['end_time']
        # expected =timezone.now()+timedelta(minutes=time_left_in_seconds(timer_paused)/60)
        
        self.assertEqual(output.month,expected.month)
        self.assertEqual(output.hour,expected.hour)
        self.assertEqual(output.minute,expected.minute)
        self.assertEqual(output.second,expected.second)
        self.assertEqual(timer_paused.is_paused,True)
        # print(timer_paused.paused.all())
        self.assertEqual(len(timer_paused.paused.all()),2)
    
       # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        status_request = self.factory.get('/pomo/timer/status')
        # calculating end_time when paused
        status_timer= Timer.objects.first()
        output= status_request.data['end_time']
        expected =timezone.now()+timedelta(minutes=time_left_in_seconds(status_timer)/60)
        self.assertEqual(output.date(),expected.date())
        self.assertEqual(output.month,expected.month)
        self.assertEqual(output.hour,expected.hour)
        self.assertAlmostEquals(output.minute,expected.minute)
        # self.assertEqual(output.second,expected.second)

class TaskTestCase(TestCase):
    def setUp(self):
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        # print(login.status_code,login.data['access'])
        self.factory.credentials(AUTHORIZATION='Bearer '+login.data['access'])
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
        # 
        # Task select test
        task_select = self.factory.post('/pomo/task/selected',{'task':Task.objects.first().id,})
        self.assertEqual(task_select.status_code,202)
        # self.assertEqual(task_select.data)


class Helper:
    def __init__(self):
        self._user_1 = User.objects.create_user(username='testuser1',password='testpassword')

    def time_diff_creator(self,days_from_now,timer_diff):
        times = (timezone.now()-timedelta(days=days_from_now),timezone.now()-timedelta(days=days_from_now)+timedelta(minutes=25))
    # def create_user(self):
        # self._user=User.objects.create_user(username='testuser',password='testpassword')

    def create_tasks(self,user):
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
        task_1=Task.objects.create(title='Task1',description='1',want_to_focus=1,user=user)
        timer_1 = Timer.objects.create(start_time=timezone.now()-timedelta(days=1),end_time=timezone.now()-timedelta(days=1)+timedelta(minutes=25),user=user)
        task_timer = TaskTimer.objects.create(task=task_1,timer=timer_1)
        
class TestDashboardData(TestCase):
    def setUp(self) -> None:
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        self.user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        print(login.status_code,login.data['access'])
        self.factory.credentials(Authorization='Bearer '+login.data['access'])  
        # Task
        task_data= [{'title':'Task One','description':'Complete this today','want_to_focus':1},
                    {'title':'Task Two','description':'Complete this today','want_to_focus':2},
                    {'title':'Task Three','description':'Complete this today','want_to_focus':3}]
        requests = []
        for i in task_data:
            print(i,'dataaaaaa')
            req = self.factory.post('/pomo/task/create',i,format='json')
            self.assertEqual(req.status_code,201)
            requests.append(req)
        # Timer( default 25)
        # start_timer = self.factory.post('/pomo/timer/start',{'task':1})
        # pause_timer = self.factory.post('/pomo/timer/update',{'state':'pause','timer':1})
        # creating  custom timer instance which are valid
        # Continued - starting 6 hours before 
        timer_one = Timer(start_time=timezone.now()-timedelta(hours=6),end_time=timezone.now()-timedelta(hours=5)+timedelta(minutes=25),user=self.user)
        timer_one.save()
        task_timer_one = TaskTimer(task=Task.objects.get(id=1),timer=timer_one)
        task_timer_one.save()
        # Two Pauses - starting 5 hours before
        timer_two_time = timezone.now()-timedelta(hours=5)
        timer_two =Timer(start_time=timer_two_time,user=self.user,end_time=timer_two_time+timedelta(minutes=25))
        timer_two.save()
        # First Pause 
        timer_two_pause_one = Paused(start_time=timer_two_time+timedelta(minutes=1),end_time= timer_two_time+timedelta(minutes=2),is_active=True)
        timer_two_time+=timedelta(minutes=2)
        timer_two.end_time = timer_two.end_time +timedelta(minutes=2)
        timer_two_pause_one.save()
        timer_two.paused.add(timer_two_pause_one)
        timer_two.save()
        task_timer_two = TaskTimer(task=Task.objects.get(id=1),timer=timer_two)
        task_timer_two.save()
        # Second Pause
        timer_two_pause_two = Paused(start_time=timer_two_time+timedelta(minutes=1),end_time = timer_two_time+timedelta(minutes=5),is_active=True)
        timer_two_pause_two.save()
        timer_two.end_time = timer_two.end_time +timedelta(minutes=5)
        timer_two.paused.add(timer_two_pause_two)
        timer_two.save()
        
        self.assertEqual(timer_two.paused.all().count(),2)
        
        
    def test_valid(self):
        resp = self.factory.get('/pomo/dashboard/')
        self.assertEqual(resp.status_code,200)
        print(resp.data,'output')
        import pprint
        pprint.pprint(resp.data)
        self.assertEqual(len(resp.data['data']),2)
        


class TestBreakAPIView(TestCase):
    def test_break(self):
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        self.user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        self.factory.credentials(authorization='Bearer '+login.data['access'])  
        res = self.factory.post('/pomo/break/create',{'break_type':'LONG'})
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['start_time'].date(),timezone.now().date())
        # Status
        status = self.factory.get('/pomo/timer/status')
        self.assertEqual(status.status_code,200)
        self.assertEqual(status.data['break_type'],'LONG')
        # Break stop
        res = self.factory.post('/pomo/break/stop',{'break':1})
        self.assertEqual(res.status_code,200)
        # Testing status when no break
        status = self.factory.get('/pomo/timer/status')
        self.assertEqual(status.status_code,200)
        self.assertEqual(status.data['status'],'Nothing')

        
