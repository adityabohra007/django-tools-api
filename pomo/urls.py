from .api import *
from django.urls import path

urlpatterns = [
    path("task/create", CreateTaskView.as_view(), name=""),
    path("task/list", ListTaskView.as_view(), name=""),
    path("task", TaskView.as_view(), name=""),
    # path("task/delete", Dele.as_view(), name="")
    path("task/selected", TaskSelectedView.as_view(), name=""),
    path("task/checkoff",TaskCheckOffApiView.as_view(), name=""),
    path("task/timer", TaskTimerView.as_view(), name=""),
    path("dashboard/", DashboardAPIView.as_view(), name=""),
    
    path('timer/start',StartTimeView.as_view(),name='start_timer'),
    path("timer/update", UpdateTimeView.as_view(), name=""),
    path("timer/status", TimerStatus.as_view(), name=""),
    
    path("configuration/", ConfigApiView.as_view(), name=""),
    path("configuration/update/", ConfigUpdateAPIView.as_view(), name=""),

path("break/create", CreateBreakView.as_view(), name=""),
path("break/stop", PauseBreakView.as_view(), name=""),

path("task/template", TemplateAPI.as_view(), name=""),
path('task/checkoff/reset',RemoveCheckOff.as_view())
]
