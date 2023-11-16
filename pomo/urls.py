from .api import *
from django.urls import path

urlpatterns = [
    path("task/create", CreateTaskView.as_view(), name=""),
    path("task/list", ListTaskView.as_view(), name=""),
    path("task", TaskView.as_view(), name=""),

    path('timer/start',StartTimeView.as_view(),name='start_timer'),
    path("timer/update", UpdateTimeView.as_view(), name=""),
    path("timer/status", TimerStatus.as_view(), name="")

]
