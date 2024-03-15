from django.test import TestCase
from rest_framework.test import APITestCase
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
import datetime

class Authentication(TestCase):
    def auth(self):
        pass

def create_timer_methods(task,start_time=timezone.now(),timer_period=25,pauses=0,pause_times=[],completed_mode=False,user=None):
    timer =Timer(start_time=start_time,end_time=timezone.now()+datetime.timedelta(minutes=timer_period),user=user)
    timer.save()
    tasktimer= TaskTimer(task=task,timer=timer)
    tasktimer.save()
    return timer
    # if pauses:
    #     for i in pause_times:
    #         p = Paused(start_time=timezone.now()+datetime.timedelta(minutes=pause_times[i]))
    #         p.save()
            # timer.paused.add(p)
            
class TimerMethods:
    def __init__(self,test_mode=False) -> None:
        pass
        
    def time_status_checking(self):
        status_request = self.factory.get('/pomo/timer/status')
        # calculating end_time when paused
        status_timer= Timer.objects.last()
        self.assertEqual(status_request.status_code,200)
        print('status checking ------',status_request.data)
        if status_request.data['status']!='Nothing':
            print('Going in-----')
            output= status_request.data['end_time']
            expected =timezone.now()+timedelta(minutes=time_left_in_seconds(status_timer)/60)
            self.assertEqual(output.date(),expected.date())
            self.assertEqual(output.month,expected.month)
            self.assertEqual(output.hour,expected.hour)
            self.assertAlmostEquals(output.minute,expected.minute)
            self.assertEqual(output.second,expected.second)
            
    def timer_start(self):
        request = self.factory.post('/pomo/timer/start',{'start_time':timezone.now(),'task':1})
        timer = Timer.objects.last()
        self.assertTrue(timer.id)
        
    def timer_update(self,state,current_time,timer,count=1):
        pause_request = self.factory.post('/pomo/timer/update',{'state':state,'current_time':current_time,'timer':timer})
        timer_paused = Timer.objects.get(id=timer)
        if state == 'completed':
            self.assertTrue(timer_paused.is_completed)
            return

        # if state == 'pause':
        self.assertEqual(timer_paused.is_paused, True if state=='pause' else False)# is_paused
        self.assertEqual(len(timer_paused.paused.all()),count)
        # self.assertEqual(timer_paused.paused.first().end_time,None)
        end_time_check = timer_paused.paused.last()
        if state=='pause':
            self.assertEqual(end_time_check.end_time,None)
        else:
            self.assertTrue(end_time_check.end_time)
            
class TimerAllStateTestCase(APITestCase,TimerMethods):

    def setUp(self):
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        self.user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()

        # print(task_request.body)
    def test_final(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        login = client.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        self.assertEqual(login.status_code,200)
        client.credentials(
            HTTP_AUTHORIZATION="Token " + login.data["access"]
        )
        # End Auth
        resp =client.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},)
        print('checking headers',resp.headers)
        self.assertEqual(resp.status_code,201)

    def test_auth(self):
        client = APIClient(enforce_csrf_checks=True)
        # login = client.login(username='testuser',password='testpassword')
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})

        token = login.data['access']
        jwtclient = APIClient(enforce_csrf_checks=True)
        resp =jwtclient.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3})
        self.assertEqual(resp.status_code,401)
        task_request = jwtclient.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},HTTP_AUTHORIZATION='Bearer '+token)
        self.assertEqual(task_request.status_code,201)

    def test_post_request(self):
        def pause_unpause(arr=[{'sleep_after':0,'state':'pause'},{'sleep_after':0,'state':'unpause'}]):
            pass
        # Pause unpause
        login = self.factory.login(username='testuser',password='testpassword')
        # One task
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        print('jwt-auth',self.factory.cookies.keys())
        task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
        # Starting timer

        # print(task_request.status_code,'one')
        self.assertEqual(task_request.status_code,201)
        task_one = Task.objects.first()
        self.assertEqual(task_one.title,'Pomo project')
        print(timezone.now(),'starting timers----')

        self.timer_start()
        time.sleep(10) # timer running
        # Pausing
        print('Pausing--`')
        self.timer_update('pause',timezone.now()+timedelta(minutes=10),1)

        # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()

        # # Now unpausing
        print('Unpausing--')
        self.timer_update('unpause',0,timer=1)

        # Timer Status Checking
        time.sleep(2)#timer running total to 3
        # status_request = self.factory.get('/pomo/timer/status')
        self.time_status_checking()

        # # Second time pausing
        self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=1,count=2)

       # Timer Status Checking
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()
        
        self.timer_update('completed',0,1)

# class TaskTestCase(TestCase):
#     def setUp(self):
#         self.factory = APIClient()
#         theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
#         theme.save()
#         user = User.objects.create_user(username='testuser',password='testpassword')
#         config = Configuration(user=user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
#         config.save()
#         login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
#         self.assertEqual(login.status_code,200)
#         print(login.status_code,login.data['access'])
#         self.factory.credentials(HTTP_AUTHORIZATION='Bearer '+login.data['access'])
#     def test_task_create_update(self):
       
#         task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
#         self.assertEqual(task_request.status_code,201)
#         # Get for ListTaskView
#         task_list = self.factory.get('/pomo/task/list',format='json')
#         self.assertEqual(task_list.status_code,200)
#         self.assertEqual(len(task_list.data),1)
#         # Updating task data
#         task_request = self.factory.put('/pomo/task',{'task':1,'title':'X',},format='json')
#         self.assertEqual(task_request.status_code,202)
#         self.assertEqual(Task.objects.get(id=1).title,'X')
#         # Updating want_to_focus
#         task_request = self.factory.put('/pomo/task',{'task':1,'want_to_focus':4,},format='json')
#         self.assertEqual(task_request.status_code,202)
#         self.assertEqual(Task.objects.get(id=1).want_to_focus,4)
#         task_request = self.factory.put('/pomo/task',{'task':1,'want_to_focus':1,},format='json')
#         self.assertEqual(task_request.status_code,202)
#         self.assertEqual(Task.objects.get(id=1).want_to_focus,1)
        
#         # Deleting a task  : It wont delete a task since we want to show the history therefore we will add is_deleted to just show that task is not in list
#         # but also need to add a method to wipe the task off the system
#         # 
#         # Task select test
#         task_select = self.factory.post('/pomo/task/selected',{'task':Task.objects.first().id,})
#         self.assertEqual(task_select.status_code,202)
#         # self.assertEqual(task_select.data)


# class Helper:
#     def __init__(self):
#         self._user_1 = User.objects.create_user(username='testuser1',password='testpassword')

#     def time_diff_creator(self,days_from_now,timer_diff):
#         times = (timezone.now()-timedelta(days=days_from_now),timezone.now()-timedelta(days=days_from_now)+timedelta(minutes=25))
#     # def create_user(self):
#         # self._user=User.objects.create_user(username='testuser',password='testpassword')

#     def create_tasks(self,user):
#         task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
#         self.assertEqual(task_request.status_code,201)
#         # Get for ListTaskView
#         task_list = self.factory.get('/pomo/task/list',format='json')
#         self.assertEqual(task_list.status_code,200)
#         self.assertEqual(len(task_list.data),1)
#         # Updating task data
#         task_request = self.factory.put('/pomo/task',{'task':1,'title':'X',},format='json')
#         self.assertEqual(task_request.status_code,202)
#         self.assertEqual(Task.objects.get(id=1).title,'X')
#         # Updating want_to_focus
#         task_request = self.factory.put('/pomo/task',{'task':1,'want_to_focus':4,},format='json')
#         self.assertEqual(task_request.status_code,202)
#         self.assertEqual(Task.objects.get(id=1).want_to_focus,4)
#         task_request = self.factory.put('/pomo/task',{'task':1,'want_to_focus':1,},format='json')
#         self.assertEqual(task_request.status_code,202)
#         self.assertEqual(Task.objects.get(id=1).want_to_focus,1)
#         task_1=Task.objects.create(title='Task1',description='1',want_to_focus=1,user=user)
#         timer_1 = Timer.objects.create(start_time=timezone.now()-timedelta(days=1),end_time=timezone.now()-timedelta(days=1)+timedelta(minutes=25),user=user)
#         task_timer = TaskTimer.objects.create(task=task_1,timer=timer_1)
        
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
        #  Compeleted
        timer_two.is_completed=True
        timer_two.completion_time=timezone.now()
        timer_two.save()
        
        self.assertEqual(timer_two.paused.all().count(),2)
        
        
    def test_valid(self):
        resp = self.factory.get('/pomo/dashboard/')
        self.assertEqual(resp.status_code,200)
        print(resp.data,'output')
        import pprint
        print('dashboard-----')
        self.assertEqual(resp.data['data'][1]['timer']['is_completed'],True)
        self.assertEqual(len(resp.data['data']),2)
        


# class TestBreakAPIView(TestCase):
#     def test_break(self):
#         self.factory = APIClient()
#         theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
#         theme.save()
#         self.user = User.objects.create_user(username='testuser',password='testpassword')
#         config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
#         config.save()
#         login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
#         self.factory.credentials(authorization='Bearer '+login.data['access'])  
#         res = self.factory.post('/pomo/break/create',{'break_type':'LONG'})
#         self.assertEqual(res.status_code,201)
#         self.assertEqual(res.data['start_time'].date(),timezone.now().date())
#         # Status
#         status = self.factory.get('/pomo/timer/status')
#         self.assertEqual(status.status_code,200)
#         self.assertEqual(status.data['break_type'],'LONG')
#         # Break stop
#         res = self.factory.post('/pomo/break/stop',{'break':1})
#         self.assertEqual(res.status_code,200)
#         # Testing status when no break
#         status = self.factory.get('/pomo/timer/status')
#         self.assertEqual(status.status_code,200)
#         self.assertEqual(status.data['status'],'Nothing')

        

class TestTemplateApiview(TestCase):
    def setUp(self):
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        self.user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()
    
    def test_get(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        login = client.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})
        self.assertEqual(login.status_code,200)
        client.credentials(
            HTTP_AUTHORIZATION="Token " + login.data["access"]
        )
        # End Auth
    def test_post(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})

        token = login.data['access']
        jwtclient = APIClient(enforce_csrf_checks=True)
        resp =jwtclient.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3})
        self.assertEqual(resp.status_code,401)
        task_request = jwtclient.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},HTTP_AUTHORIZATION='Bearer '+token)
        self.assertEqual(task_request.status_code,201)
        # End Auth
        # resp =client.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},)
        # print('checking headers',resp.headers)
        # self.assertEqual(resp.status_code,201)
        # now calling template
        req = jwtclient.post('/pomo/task/template',{'name':'TestTemplate'},HTTP_AUTHORIZATION='Bearer '+token)
        self.assertEqual(req.status_code,201)
        
        # Should save all currently active template to template
    

# class TestBarChart(APITestCase,TimerMethods):
#     def setUp(self):
#         self.factory = APIClient()
#         theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
#         theme.save()
#         self.user = User.objects.create_user(username='testuser',password='testpassword')
#         config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
#         config.save()

#     def test_auth(self):
#         # login = client.login(username='testuser',password='testpassword')
#         #Unauthorized 
#         t = self.factory.get('/pomo/dashboard/barchart')
#         self.assertEqual(t.status_code,401)
#         # Authorized
#         login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})# Login here

#         token = login.data['access']
#         jwtclient = APIClient(enforce_csrf_checks=True)
#         resp =jwtclient.get('/pomo/dashboard/barchart',HTTP_AUTHORIZATION='Bearer '+token)# First method to authenticate
#         self.assertEqual(resp.status_code,400)
        
#         # Pre
#         t = self.factory.get('/pomo/dashboard/barchart') # Second method to authenticate so that just login than use factor
#         self.assertEqual(t.status_code,400)
#         task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
#         # Starting timer

#         # print(task_request.status_code,'one')
#         self.assertEqual(task_request.status_code,201)
#         # Create Atleast 20 Timers
        
#         # week
#         resp =jwtclient.get('/pomo/dashboard/barchart',{'mode':'Week'},HTTP_AUTHORIZATION='Bearer '+token)
#         self.assertEqual(resp.status_code,200)
        
#         # Starting timer
        
#         # print(task_request.status_code,'one')
#         self.assertEqual(task_request.status_code,201)
#         task_one = Task.objects.first()
#         self.assertEqual(task_one.title,'Pomo project')
#         print(timezone.now(),'starting timers----')
#         timer1 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=7),user=User.objects.get(id=1))
#         # self.timer_start()
#         # time.sleep(1) # timer running
#         # Pausing
#         print('Pausing--`')
#         self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer1.id)

#         # Timer Status Checking 
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()

#     #     # # Now unpausing
#     #     print('Unpausing--')
#         self.timer_update('unpause',0,timer=timer1.id)

#         # Timer Status Checking
#         time.sleep(2)#timer running total to 3
#         # status_request = self.factory.get('/pomo/timer/status')
#         self.time_status_checking()

#         # # Second time pausing
#         self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer1.id,count=2)

#        # Timer Status Checking
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()
        
#         self.timer_update('completed',0,timer1.id)
#         print(Timer.objects.filter().values(),'testing-----')
#         resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Week'})
#         self.assertEqual(resp.status_code,200)
        
#         timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=0),user=User.objects.get(id=1))
#         # self.timer_start()
#         # time.sleep(1) # timer running
#         # Pausing
#         print('Pausing--`')
#         self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

#         # Timer Status Checking 
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()

#     #     # # Now unpausing
#     #     print('Unpausing--')
#         self.timer_update('unpause',0,timer=timer2.id)

#         # Timer Status Checking
#         time.sleep(2)#timer running total to 3
#         # status_request = self.factory.get('/pomo/timer/status')
#         self.time_status_checking()

#         # # Second time pausing
#         self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

#        # Timer Status Checking
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()
        
#         self.timer_update('completed',0,timer2.id)
#         print(Timer.objects.filter().values(),'testing-----')
#         resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Week'})
#         self.assertEqual(resp.status_code,200)
#         # This is to test if includes this data in final output

#         timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=10),user=User.objects.get(id=1))
#         # self.timer_start()
#         # time.sleep(1) # timer running
#         # Pausing
#         print('Pausing--`')
#         self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

#         # Timer Status Checking 
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()

#     #     # # Now unpausing
#     #     print('Unpausing--')
#         self.timer_update('unpause',0,timer=timer2.id)

#         # Timer Status Checking
#         time.sleep(2)#timer running total to 3
#         # status_request = self.factory.get('/pomo/timer/status')
#         self.time_status_checking()

#         # # Second time pausing
#         self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

#        # Timer Status Checking
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()
        
#         self.timer_update('completed',0,timer2.id)
#         print(Timer.objects.filter().values(),'testing-----')
#         resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Week'})
#         self.assertEqual(resp.status_code,200)

#         # Check if after today is included
#         timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()+datetime.timedelta(days=1),user=User.objects.get(id=1))
#         # self.timer_start()
#         # time.sleep(1) # timer running
#         # Pausing
#         print('Pausing--`')
#         self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

#         # Timer Status Checking 
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()

#     #     # # Now unpausing
#     #     print('Unpausing--')
#         self.timer_update('unpause',0,timer=timer2.id)

#         # Timer Status Checking
#         time.sleep(2)#timer running total to 3
#         # status_request = self.factory.get('/pomo/timer/status')
#         self.time_status_checking()

#         # # Second time pausing
#         self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

#        # Timer Status Checking
#         print('Status--')
#         time.sleep(2) # pause time
#         self.time_status_checking()
        
#         self.timer_update('completed',0,timer2.id)
#         print(Timer.objects.filter().values(),'testing-----')
#         resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Week'})
#         self.assertEqual(resp.status_code,200)
        
        
#         # task_request = jwtclient.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},HTTP_AUTHORIZATION='Bearer '+token)
#         # self.assertEqual(task_request.status_code,201)
class TestBarChartMonth(APITestCase,TimerMethods):
    def setUp(self):
        self.factory = APIClient()
        theme = Theme(short_break='#aaaa',long_break='#cbcd',pomodoro='#edac')
        theme.save()
        self.user = User.objects.create_user(username='testuser',password='testpassword')
        config = Configuration(user=self.user,theme=theme,pomo_time=25,short_break_time=5,long_break_time=10)
        config.save()
    def test_month(self):
        
        # t = self.factory.get('/pomo/dashboard/barchart')
        # self.assertEqual(t.status_code,401)
        # Authorized
        login = self.factory.post('/dj-rest-auth/login/',{'username':'testuser','password':'testpassword'})# Login here

        token = login.data['access']
        jwtclient = APIClient(enforce_csrf_checks=True)
        resp =jwtclient.get('/pomo/dashboard/barchart',HTTP_AUTHORIZATION='Bearer '+token)# First method to authenticate
        self.assertEqual(resp.status_code,400)
        
        # Pre
        task_request = self.factory.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},format='json')
        # Starting timer

        self.assertEqual(task_request.status_code,201)
        # Create Atleast 20 Timers
        
        # week
        resp =jwtclient.get('/pomo/dashboard/barchart',{'mode':'Week'},HTTP_AUTHORIZATION='Bearer '+token)
        self.assertEqual(resp.status_code,200)
        
        # Starting timer
        
        # print(task_request.status_code,'one')
        self.assertEqual(task_request.status_code,201)
        task_one = Task.objects.first()
        self.assertEqual(task_one.title,'Pomo project')
        # print(timezone.now(),'starting timers----')
        timer1 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=4),user=User.objects.get(id=1))
        self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer1.id)
        time.sleep(2) # pause time
        self.time_status_checking()
        self.timer_update('unpause',0,timer=timer1.id)
        # Timer Status Checking
        time.sleep(2)#timer running total to 3
        # self.time_status_checking()

        # # Second time pausing
        self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer1.id,count=2)

       # Timer Status Checking
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()
        
        self.timer_update('completed',0,timer1.id)
    #     print(Timer.objects.filter().values(),'testing-----')
    #     resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Week'})
    #     self.assertEqual(resp.status_code,200)
        
        timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=5),user=User.objects.get(id=1))
        # self.timer_start()
        # time.sleep(1) # timer running
        # Pausing
        print('Pausing--`')
        self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

        # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()

    #     # # Now unpausing
    #     print('Unpausing--')
        self.timer_update('unpause',0,timer=timer2.id)

        # Timer Status Checking
        time.sleep(2)#timer running total to 3
        # status_request = self.factory.get('/pomo/timer/status')
        self.time_status_checking()

        # # Second time pausing
        self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

       # Timer Status Checking
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()
        
        self.timer_update('completed',0,timer2.id)
        # print(Timer.objects.filter().values(),'testing-----')
        # resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Week'})
        # self.assertEqual(resp.status_code,200)
        timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=29),user=User.objects.get(id=1))
        # self.timer_start()
        # time.sleep(1) # timer running
        # Pausing
        print('Pausing--`')
        self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

        # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()

    #     # # Now unpausing
    #     print('Unpausing--')
        self.timer_update('unpause',0,timer=timer2.id)

        # Timer Status Checking
        time.sleep(2)#timer running total to 3
        # status_request = self.factory.get('/pomo/timer/status')
        self.time_status_checking()

        # # Second time pausing
        self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

       # Timer Status Checking
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()
        
        self.timer_update('completed',0,timer2.id)
        # print(Timer.objects.filter().values(),'testing-----')
        # resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Month'})
        # self.assertEqual(resp.status_code,200)
    #     # This is to test if includes this data in final output
        # ---NEW INSTANCE---
        timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()-datetime.timedelta(days=10),user=User.objects.get(id=1))
        # self.timer_start()
        # time.sleep(1) # timer running
        # Pausing
        print('Pausing--`')
        self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

        # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()

    #     # # Now unpausing
    #     print('Unpausing--')
        self.timer_update('unpause',0,timer=timer2.id)

        # Timer Status Checking
        time.sleep(2)#timer running total to 3
        # status_request = self.factory.get('/pomo/timer/status')
        self.time_status_checking()

        # # Second time pausing
        self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

       # Timer Status Checking
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()
        
        self.timer_update('completed',0,timer2.id)
        # print(Timer.objects.filter().values(),'testing-----')
        # resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Month'})
        # self.assertEqual(resp.status_code,200)

        # Check if after today is included
        # ---NEW INSTANCE---
        timer2 = create_timer_methods(task=Task.objects.first(),start_time=timezone.now()+datetime.timedelta(days=1),user=User.objects.get(id=1))
        # self.timer_start()
        # time.sleep(1) # timer running
        # Pausing
        print('Pausing--`')
        self.timer_update('pause',timezone.now()+timedelta(minutes=10),timer2.id)

        # Timer Status Checking 
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()

    #     # # Now unpausing
    #     print('Unpausing--')
        self.timer_update('unpause',0,timer=timer2.id)

        # Timer Status Checking
        time.sleep(2)#timer running total to 3
        # status_request = self.factory.get('/pomo/timer/status')
        self.time_status_checking()

        # # Second time pausing
        self.timer_update('pause',timezone.now()+timedelta(minutes=2),timer=timer2.id,count=2)

       # Timer Status Checking
        print('Status--')
        time.sleep(2) # pause time
        self.time_status_checking()
        
        self.timer_update('completed',0,timer2.id)
        print(Timer.objects.filter().values(),'testing-----')
        resp =self.factory.get('/pomo/dashboard/barchart',{'mode':'Month'})
        self.assertEqual(resp.status_code,200)
        print(resp.data,'barchart-data')
        # self.assertEqual(len(resp.data.items()),5)
        
        
        
        # task_request = jwtclient.post('/pomo/task/create',{'title':'Pomo project','description':'Complete this today','want_to_focus':3},HTTP_AUTHORIZATION='Bearer '+token)
        # self.assertEqual(task_request.status_code,201)
        