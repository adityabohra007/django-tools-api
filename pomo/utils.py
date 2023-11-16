from .models import Timer
def check_if_any_timer_already_active(current_time):
    '''Current time to be taken from user in api'''
    if Timer.objects.filter(end_time__gt=current_time,is_completed=False).count() :
        # so that if end_time is still more but checked as completed then it will be shown as timer is stopped
        return True
    else:
        return False