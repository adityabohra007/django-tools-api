from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from .utils import parse_date,parse_datetime_with_timezone,time_left_in_seconds
from django.utils import timezone
from django.db import transaction
# from django.db.transaction import atomic
from .models import *
import datetime
from .utils import check_if_any_timer_already_active
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.jwt_auth import JWTAuthentication,JWTCookieAuthentication
# right now working on guest user only 

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView): # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://127.0.0.1:8081/accounts/google/login/callback/'
    client_class = OAuth2Client


class ListTaskView(generics.ListAPIView):
    serializer_class = TaskDataSerializer
    def get_queryset(self):
        return Task.task.active()
    
class CreateTaskView(APIView):
    permission_classes=[IsAuthenticated]
    # authentication_classes=[]
    def post(self,request):
        print('running')
        data= request.data
        # data['user'] = request.user.id
        # return Response(status=status.HTTP_200_OK)
        

        serializer_class = TaskSerializer(
                                          data={'user':request.user.id,
                                                                  'title':data['title'],
                                                                  'want_to_focus':data['want_to_focus'],
                                                                  'description':data['description']
                                                                  })
        if serializer_class.is_valid():
        # serializer_class
            try:
                with transaction.atomic():
                    instance = serializer_class.save()
                    tp = TaskPosition(task=instance,position=0)
                    tp.save()
                    return Response(status=status.HTTP_201_CREATED)

            except:
                print('Error saving')
                return Response(status=status.HTTP_403_FORBIDDEN)
                # Time also have to be supplied from frontend
                # time_serializer = TimerSerializer(data=request.data)
                # if time_serializer.is_valid():
                #     timer_saved = time_serializer.save()
                #     tt = TaskTimer(task=instance,timer=timer_saved)
                #     tt.save()

        else:
            print(serializer_class.errors)
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class TaskTimerView(APIView):
    def get(self,request):
        t = timezone.now()
        query = TaskTimer.objects.filter(
            task__user=request.user
            ).filter(
            Q(timer__start_time__date=t.date(),timer__end_time__lt=t)|
            Q(timer__start_time__date=t.date(),timer__is_completed=True)
            )
        ser = TaskTimerSerializer(query,many=True)
        return Response(ser.data,status=status.HTTP_200_OK)
        
class TaskView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=(IsAuthenticated,)

    def put(self,request):
        print(request.data.get('id'))
        if not request.data.get('id'):
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        instance= Task.objects.get(id=int(request.data.get('id')))
        serializer_class = TaskSerializer(user=request.user,instance=instance,data=request.data,partial=True)
        if serializer_class.is_valid():
            instance = serializer_class.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        print(serializer_class.error_messages)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    
    def delete(self, request, *args, **kwargs):
        if not request.data.get('task'):
            pass
        task = Task.objects.get(id=int(request.data.get('task')))
        task.is_deleted=True
        task.save()
        return Response(status=status.HTTP_202_ACCEPTED)

def get_current_running_time(start_time):
    pass
def any_time_active():
    pass

class ThemeApiView(APIView):
    pass
class ConfigApiView(APIView):
    permission_classes=(IsAuthenticated,)
    # authentication_classes=[JWTCookieAuthentication]
    def get(self,request):
        ser = ConfigurationSerializer(instance=Configuration.objects.get(user=request.user))
        return Response({'data':ser.data},status=status.HTTP_200_OK)
class ConfigUpdateAPIView(APIView):
    def post(self,request):
        print(request.data,request.POST,'updating config')
        config = Configuration.objects.get(user=request.user)
        ser = ConfigurationUpdateSerializer(instance=config,data=request.data)
        if ser.is_valid():
            theme_ser = ThemeSerializer(instance=config.theme,data=request.data['theme'])
            if theme_ser.is_valid():
                theme_ser.save()
                ser.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                print(theme_ser.errors)
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            print(ser.errors)
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
class TaskCheckOffApiView(APIView):
    permission_classes=(IsAuthenticated,)
    def post(self,request):
        ser = TaskCheckOffSerializer(instance = Task.objects.get(id=request.data.get('id')),data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
class TaskSelectedView(APIView):
    permission_classes=(IsAuthenticated,)

    def get(self,request):
        instance = TaskSelected.objects.filter() #filter(user =request.user)
        if instance.count():
            ser = TaskSelectedSerializer(instance=instance.first())
            return Response({'selected':ser.data},status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK)
    def post(self,request):
        task_id = request.data.get('task')
        task = Task.objects.filter(id=int(task_id))
        user=User.objects.first()
        taskSelect = TaskSelected.objects.filter(user=user)
        if taskSelect.count():
            taskSelect=taskSelect.get()
            taskSelect.task=task.get()
        else:
            taskSelect = TaskSelected(user=user,task=task.get())
        taskSelect.save()
        # ser = TaskSelectedSerializer(instance=taskSelect)
        return Response(status=status.HTTP_202_ACCEPTED)
        
class TimerStatus(APIView):
    '''
    Send timer end_time,status
    '''
    permission_classes=[IsAuthenticated]
    def get(self,request):
        # return Response()
        print(request.GET.get('current_time'),'current')
        # Added paused filter 
        current = parse_datetime_with_timezone('')#request.GET.get('current_time'))
        instance =Timer.objects.filter(is_completed=False,user=request.user).order_by('-start_time')
        # Timer.objects.filter(
        #     # Q(end_time__gt=parse_datetime_with_timezone(request.GET.get('current_time')))&Q(is_completed=False)|
        #     # (Q(end_time__lt=parse_datetime_with_timezone(request.GET.get('current_time')))&Q(is_completed=False)&Q(is_paused=True))
            
        #     ).order_by('-start_time').exclude(is_completed=True).filter(Q(is_paused=True)&Q(end_time__lt=current)|Q(is_paused=True)&Q(end_time__gt=current)) #.exclude(is_paused=True,end_time__gt=parse_datetime_with_timezone(request.GET.get('current_time')))
        print(instance)
        instance = check_if_any_timer_already_active(timezone.now())

        if instance :
            instance=instance.first()
            print(instance.start_time,instance.end_time)

            timer_status ='paused' if instance.is_paused else 'running'
            if timer_status=='paused':
                ser = TimerDataSerializer(instance=instance)
                # end_time = get_time_left(instance,current)
                end_time=timezone.now()+datetime.timedelta(minutes=time_left_in_seconds(instance)/60)
                print(end_time,'get_time_left')
                return Response( {'end_time':end_time,'id':instance.id, 'status':timer_status,'timer':ser.data})
            else:
                return Response( {'end_time':instance.end_time,'id':instance.id, 'status':timer_status,})
        else:
            break_instance = Break.objects.filter(user=request.user,end_time__gt=timezone.now())
            if break_instance.count():
                break_ser = BreakSerializer(instance=break_instance.get())
                return Response(break_ser.data,status=status.HTTP_200_OK)
            return Response({'status':'Nothing'})
        timer = Timer.objects.get(id=int(timer))
        if timer.is_completed:
            return Response({'status':'completed'},status=status.HTTP_200_OK)
        time_left= 0
        # print(sum([i.end_time - i.start_time for i in timer.paused.all()]))
        time_left = ((timer.end_time - timer.start_time)) #- sum([i.end_time - i.start_time for i in timer.paused.all()])
        serializer = TimerDataSerializer(instance=timer)
        
        return Response({"data":serializer.data,'time_left':time_left})
class StartTimeView(APIView):
    permission_classes=[IsAuthenticated]
    ''' Timer frontend -
        If not authenticated just start timer without backend api
        Condition :
        check if any timer are active
    '''
    def post(self,request):
        print(request.data,'ddddddd',request.data.get('start_time'))
        start_time = parse_datetime_with_timezone(request.data.get('start_time'))
        if check_if_any_timer_already_active(start_time):
            print('already')
            return Response(status=status.HTTP_403_FORBIDDEN)
        timer_serializer = TimerSerializer(user=request.user,data={'start_time':start_time,'user':request.user.id}) # start time 
        if not request.data.get('task'):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if timer_serializer.is_valid():
            try:
                with transaction.atomic():
                    timer = timer_serializer.save()
                    timer.end_time = timer.start_time + datetime.timedelta(minutes=Configuration.objects.first().pomo_time)
                    timer.is_active = True # to  show that timer is active and not completed by force
                    timer.save()
                    print(timer)
                    task = Task.objects.get(id=int(request.data.get('task')))
                    time_task = TaskTimer(timer=timer,task=task)
                    time_task.save()
                    return Response({'end_time':timer.end_time,'id':timer.id},status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            print(timer_serializer.errors)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UpdateTimeView(APIView):
    '''State data - pause
                  - completed
    '''
    permission_classes=[IsAuthenticated]

    def post(self,request):
        current_time =parse_datetime_with_timezone('')
        timer = request.data.get('timer')
        print(timer,request.data,'pausing')
        timer = Timer.objects.get(id=int(timer))
        if request.data.get('state'):
            state = request.data.get('state')
            if state == 'pause':
                print(state)
                # Check if already paused
                paused = Paused(start_time=current_time)
                paused.save()
                timer.is_paused = True
                timer.save()
                timer.paused.add(paused)
                timer.save()
                # timer.paused.
                return Response(status=status.HTTP_200_OK)

            elif state == 'unpause':
                # time is increasing here please check-------
                #If not paused  reject
                # end_time = request.POST.get('end_time')
                if not current_time:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                if timer.is_paused:
                    paused = timer.paused.all()
                    paused_instance= None
                    for i in paused:
                        # Find if any have end_time == none
                        if i.end_time == None:
                            paused_instance=i  
                    print(paused_instance,'pause_instance')
                    if paused_instance:
                        # use end_time to add the time to that instance
                        paused_instance.end_time = current_time
                        paused_instance.save()
                        timer.is_paused=False
                        time_count = 0
                        print([(i.start_time,i.end_time) for i in timer.paused.all()])
                        for i in timer.paused.all():
                            try:
                                time_count+= (i.end_time-i.start_time ).total_seconds()//60
                            except Exception as e:
                                print(e,'exception')
                        print(time_count,'time_count')
                        timer.end_time=timezone.now()+datetime.timedelta(minutes=time_left_in_seconds(instance=timer)/60)
 # now start_time  to end_time ,subtract pause_time (add all time from all pause time ) to find total time completed
                        # paused_instance.save()
                        timer.save()
                        ser = TimerDataSerializer(instance=timer)
                        return Response(
                            {'timer':ser.data},
                            status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            elif state == 'completed':
                completion_time = timezone.now()
                timer.completion_time = completion_time
                timer.is_completed = True
                timer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error':'state field not found'},status=status.HTTP_400_BAD_REQUEST)
# class StopTimeView(generics.UpdateAPIView):
#     pass

def calculate_end_time():
    pass
class CreateBreakView(APIView):
    '''Long/short '''
    permission_classes=[IsAuthenticated]
    def post(self,request):
        if Break.objects.filter(end_time__gt=timezone.now()).count():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not request.POST.get('break_type'):
            pass
        print(request.data.get('break_type'),'-____---___')
        instance = Break(start_time = timezone.now(),break_type =request.data.get('break_type'),user=request.user )
        config = Configuration.objects.get(user=request.user)

        if request.data.get('break_type')=='LONG':
            config = Configuration.objects.get(user=request.user)
            instance.end_time = timezone.now()+datetime.timedelta(minutes=(config.long_break_time))
        else:
            instance.end_time = timezone.now()+datetime.timedelta(minutes=(config.short_break_time))
        # if instance.val():
        instance.save()
        return Response({'end_time':instance.end_time},status=status.HTTP_201_CREATED)
        # else:
        #     return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
class PauseBreakView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        if not request.POST.get('break'):
            pass
        instance = Break.objects.get(id= int(request.POST.get('break')))
        instance.end_time = timezone.now()
        instance.save()
        return Response(status=status.HTTP_200_OK)


class SettingsAPIView(APIView):
    pass


class DashboardAPIView(APIView):
    '''
        Uses data, One day's data , timer data ,pause data ,no data compare.
        color coding , tags##. 
    '''
    permission_classes=[IsAuthenticated]
    def get(self,request):
        print(TaskTimer.objects.filter(),'dashboard tasktimer')
        t = timezone.now()
        tasktimer= TaskTimer.objects.filter(
            task__user=request.user
            ).filter(
            Q(timer__start_time__date=t.date(),timer__end_time__lt=t)|
            Q(timer__start_time__date=t.date(),timer__is_completed=True)
            )
        # task_timer = TaskTimer.objects.filter(task__user=request.user,timer__end_time__lt=timezone.now()).order_by('timer__start_time')
        ser = TaskTimerSerializer(tasktimer,many=True)
        break_instance  = Break.objects.filter(user =request.user,start_time__date=t.date(),end_time__lt=t)
        break_ser = BreakSerializer(break_instance,many=True)
        # Now make a timeline, iterate over the data and convert the 1 minute to 1px and by difference in pauses use it to show pauses and so on.
        # leave rest of the postion which was not used used as white space
        return Response({'data':ser.data,'break':break_ser.data},status=status.HTTP_200_OK)



class TemplateAPI(APIView):
    def get(self,request):
        instance = TaskTemplate.objects.filter(user = request.user)
        ser = TaskTemplateSerializer(instance,many=True)
        
        return Response({'data':ser.data}, status=status.HTTP_200_OK)
    def post(self,request):
        query = Task.objects.filter(user=request.user)
        name = request.data.get('name')
        if not name:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        template = TaskTemplate.objects.create(name=name)
        create = [
               Task(title=i.title,description=i.description,want_to_focus=i.want_to_focus,user=request.user) for i in query
        ]
        print(create,'template')
        instance = TaskTemplateItem.objects.bulk_create(create)
        for i in instance:
            template.task.add(i.id)
        print(instance,'instance')
        return Response(status=status.HTTP_201_CREATED)
    
class RemoveCheckOff(APIView):
    def post(self,request):
        task = Task.objects.filter(user=request.user,is_deleted=False,check_off=True)
        for check in task:
            check.check_off=False
            check.save()
            
        return Response(status=status.HTTP_200_OK)


# timeline api
# green for task time, gray for break,white for no task
# on hover show text, togglable .
# date on first column,
# tags-to seperate task and show total /max of which category of task is completed
