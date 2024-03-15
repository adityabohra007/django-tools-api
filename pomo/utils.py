from .models import Timer
import datetime
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Configuration
def check_if_any_timer_already_active(current_time):
    '''Current time to be taken from user in api'''
    # print(current_time,'in checking',Timer.objects.filter(end_time__gt=current_time) ,Timer.objects.filter(is_completed=False).count())
    if Timer.objects.filter(Q(end_time__gt=current_time)&Q(is_completed=False)):
        # so that if end_time is still more but checked as completed then it will be shown as timer is stopped
        return Timer.objects.filter(Q(end_time__gt=current_time)&Q(is_completed=False))
    else:
        return False
    

def parse_date(date):
    # return datetime.datetime.strptime(date,'%m/%d/%Y, %I:%M:%S %p')
    return datetime.datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%fZ")

def parse_datetime_with_timezone(date):
    # print(date,"parse_datetime_with_timezone")
    # if date.__contains__('+'):
    #     pass
    # else:
    #     new_date = []
    #     date = date.split(' ')
    #     date[-4] = '+'+date[-4]
    #     new_date= ' '.join(date[0:6])+''.join(date[6:8])+' '.join(date[8:])
    #     # date =' '.join(date)
    #     date=new_date
    # print (date)
    # return datetime.datetime.strptime(date.split('(')[0].rstrip(),"%a %b %d %Y %H:%M:%S %Z%z")
    return timezone.now()

# def total_pomo_completed(instance):
    


def time_left_in_seconds(instance):
    time_count=0
    paused = None
    config = Configuration.objects.get(user = instance.user)
    for item in instance.paused.all():
        if item.end_time==None:
            time_count+=(timezone.now()-item.start_time).total_seconds()
        else:
            time_count+=(item.end_time-item.start_time).total_seconds()
    # time_count is time wasted in pause
    total_time_from_start_to_now = (timezone.now()-instance.start_time).total_seconds()
    return config.pomo_time*60-abs(total_time_from_start_to_now-time_count)# subtracting total required pomo by time until now -paused time


# concept of time

'''
start_time

pause1-start
in-between- if checked here , calculation is on  timezone.now()+ 25*60 - (pause1-start-start_time).total_seconds()
end- if checked here ,calculate  - 25*60 - timedelta(sec=pause1-end-pause1-start) -timedelta
        total time                      wasted in pause
current_time-start_time - timedelta(sec=pause-end-pause-start)

than subtract from 25*60
than add this time to timezone.now


pause2-start
in-between
end
pause3-start
in-between
end

'''