from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework.response import Response
from .serializers import TaskSerializer,TaskDataSerializer,TimerSerializer,TimerDataSerializer
from rest_framework import status

# from django.db.transaction import atomic
from .models import *
import datetime
from .utils import check_if_any_timer_already_active
# right now working on guest user only 

class InitialViewApi(APIView):
    ''' Timer if any running
        All task list
        theme data 
    '''
    pass

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
class TimerStatus(APIView):
    def get(self,request):
        timer= request.GET.get('timer')
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
        if check_if_any_timer_already_active(request.POST.get('start_time')):
            return Response(status=status.HTTP_403_FORBIDDEN)
        timer_serializer = TimerSerializer(data=request.data) # start time 
        if not request.POST.get('task'):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if timer_serializer.is_valid():
            timer = timer_serializer.save()
            timer.end_time = timer.start_time + datetime.timedelta(minutes=25)
            timer.is_active = True # to  show that timer is active and not completed by force
            timer.save()
            print(timer)
            task = Task.objects.get(id=int(request.POST.get('task')))
            time_task = TaskTimer(timer=timer,task=task)
            time_task.save()
            return Response(status=status.HTTP_201_CREATED)
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
        current_time =request.POST.get('current_time')
        timer = request.POST.get('timer')
        timer = Timer.objects.get(id=int(timer))
        if request.POST.get('state'):
            state = request.POST.get('state')
            if state == 'pause':
                print(state)
                # Check if already paused
                paused = Paused(start_time=current_time)
                paused.save()
                timer.is_paused = True
                timer.save()
                timer.paused.add(paused)
                # timer.paused.
                return Response(status=status.HTTP_200_OK)

            elif state == 'unpause':
                #If not paused  reject
                end_time = request.POST.get('end_time')
                if not end_time:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                if timer.is_paused:
                    paused = timer.paused.all()
                    paused_instance= None
                    for i in paused:
                        # Find if any have end_time == none
                        if i.end_time == None:
                            paused_instance=i  
                    if paused_instance:
                        # use end_time to add the time to that instance
                        paused_instance.end_time = end_time
                        paused_instance.save()
                        timer.is_paused=False
                        time_count = 0
                        print([(i.start_time,i.end_time) for i in timer.paused.all()])
                        for i in timer.paused.all():
                            try:
                                time_count+= (i.end_time-i.start_time ).total_seconds()//60
                            except Exception as e:
                                print(e)
                        print(time_count,'time_count')
                        timer.end_time +=  datetime.timedelta(minutes=time_count) # now start_time  to end_time ,subtract pause_time (add all time from all pause time ) to find total time completed
                        paused_instance.save()
                        timer =timer.save()
                        ser = TimerDataSerializer(instance=timer)
                        return Response(
                            {'timer':ser.data},
                            status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            elif state == 'completed':
                completion_time = request.POST.get('completion_time')
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