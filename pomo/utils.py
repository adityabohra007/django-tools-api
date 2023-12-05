from .models import Timer
import datetime
from django.db.models import Q
def check_if_any_timer_already_active(current_time):
    '''Current time to be taken from user in api'''
    print(current_time,'in checking',Timer.objects.filter(end_time__gt=current_time) ,Timer.objects.filter(is_completed=False).count())
    if Timer.objects.filter(Q(end_time__gt=current_time)&Q(is_completed=False)):
        # so that if end_time is still more but checked as completed then it will be shown as timer is stopped
        return True
    else:
        return False
    

def parse_date(date):
    # return datetime.datetime.strptime(date,'%m/%d/%Y, %I:%M:%S %p')
    return datetime.datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%fZ")

def parse_datetime_with_timezone(date):
    print(date,"parse_datetime_with_timezone")
    if date.__contains__('+'):
        pass
    else:
        new_date = []
        date = date.split(' ')
        date[-4] = '+'+date[-4]
        new_date= ' '.join(date[0:6])+''.join(date[6:8])+' '.join(date[8:])
        # date =' '.join(date)
        date=new_date
    print (date)
    return datetime.datetime.strptime(date.split('(')[0].rstrip(),"%a %b %d %Y %H:%M:%S %Z%z")

def get_time_left(instance,current_time):
    print('get_time_left------')
    print(current_time)
    time_count=0
    for item in instance.paused.all():
        try:
            print(item.end_time,item.start_time,(item.end_time-item.start_time ).total_seconds())
            time_count+= (item.end_time-item.start_time ).total_seconds()# this difference is to be subtracted from timer's end_time-start_time value
        except Exception as e:
            current = current_time
            time_count+=(current-item.start_time).total_seconds()
            print(e,'exception:might be none')
        return current_time + datetime.timedelta(seconds=(instance.end_time-instance.start_time-datetime.timedelta(seconds=time_count)).total_seconds())
        # start_to_first_pause_diff=(instance.paused.order_by('-start_time').first().start_time-instance.start_time).total_seconds()

# if __name__=="__main__":
#     from django.utils import timezone
#     get_time_left(Timer.objects.first(),timezone.now())