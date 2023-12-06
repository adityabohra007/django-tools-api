from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework.response import Response
from .serializers import TaskSerializer,TaskDataSerializer,TimerSerializer,TimerDataSerializer,TaskSelectedSerializer,ConfigurationSerializer
from rest_framework import status
from .utils import parse_date,parse_datetime_with_timezone,time_left_in_seconds
from django.utils import timezone
# from django.db.transaction import atomic
from .models import *
import datetime
from .utils import check_if_any_timer_already_active
from django.db.models import Q
# right now working on guest user only 

class InitialViewApi(APIView):
    ''' Timer if any running
        All task list
        theme data 
    '''
    # def get(self,request):
    #     if request.data.get('current_time'):
    #         pass
    #     timer = Timer.objects.filter(is_completed=False,end_time__gt=timezone.now)

class ListTaskView(generics.ListAPIView):
    serializer_class = TaskDataSerializer
    def get_queryset(self):
        return Task.objects.filter()
    
class CreateTaskView(APIView):

    def post(self,request):
        print('running')
        serializer_class = TaskSerializer(data=request.data)
        if serializer_class.is_valid():
        # serializer_class
            instance = serializer_class.save()
            tp = TaskPosition(task=instance,position=0)
            tp.save()
            # Time also have to be supplied from frontend
            # time_serializer = TimerSerializer(data=request.data)
            # if time_serializer.is_valid():
            #     timer_saved = time_serializer.save()
                # tt = TaskTimer(task=instance,timer=timer_saved)
                # tt.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class TaskView(generics.RetrieveUpdateDestroyAPIView):
    
    def put(self,request):
        print(request.data.get('task'))
        if not request.data.get('task'):
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        instance= Task.objects.get(id=int(request.data.get('task')))
        serializer_class = TaskSerializer(instance=instance,data=request.data,partial=True)
        if serializer_class.is_valid():
            instance = serializer_class.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        print(serializer_class.error_messages)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    
    def delete(self, request, *args, **kwargs):
        if not request.data.get('task'):
            pass
        task = Task.objects.get(id=int(request.data.get('task')))
        task.delete_task=True
        task.save()
        return Response(status=status.HTTP_202_ACCEPTED)

def get_current_running_time(start_time):
    pass
def any_time_active():
    pass

class ThemeApiView(APIView):
    pass
class ConfigApiView(APIView):
    def get(self,request):
        ser = ConfigurationSerializer(instance=Configuration.objects.first())
        return Response({'data':ser.data},status=status.HTTP_200_OK)
class TaskSelectedView(APIView):
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
            taskSelect = TaskSelected(user=user,task=task)
        taskSelect.save()
        # ser = TaskSelectedSerializer(instance=taskSelect)
        return Response(status=status.HTTP_202_ACCEPTED)
        
class TimerStatus(APIView):
    '''
    Send timer end_time,status
    '''
    def get(self,request):
        # return Response()
        print(request.GET.get('current_time'),'current')
        # Added paused filter 
        current = parse_datetime_with_timezone('')#request.GET.get('current_time'))
        instance =Timer.objects.filter(is_completed=False).order_by('-start_time')
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
        timer_serializer = TimerSerializer(data={'start_time':start_time}) # start time 
        if not request.data.get('task'):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if timer_serializer.is_valid():
            timer = timer_serializer.save()
            timer.end_time = timer.start_time + datetime.timedelta(minutes=Configuration.objects.first().pomo_time)
            timer.is_active = True # to  show that timer is active and not completed by force
            timer.save()
            print(timer)
            task = Task.objects.get(id=int(request.data.get('task')))
            time_task = TaskTimer(timer=timer,task=task)
            time_task.save()
            return Response({'end_time':timer.end_time,'id':timer.id},status=status.HTTP_201_CREATED)
        else:
            print(timer_serializer.errors)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UpdateTimeView(APIView):
    '''State data - pause
                  - completed
    '''
    def post(self,request):
        if not request.POST.get('timer'):
            pass
        if not request.POST.get('current_time'):
            pass
        if not request.POST.get('completion_time'):
            pass
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
class CreateBreakView(generics.CreateAPIView):
    '''Long/short '''
    pass
class PauseBreakView(generics.UpdateAPIView):
    pass


class SettingsAPIView(APIView):
    pass




# Next to do is 
#  Initial data send api 
#Theme API
#Make it React
#