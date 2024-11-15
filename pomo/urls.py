from .api import *
from django.urls import include, path, re_path

from .api import TaskViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"task", TaskViewset, basename="task")
urlpatterns = router.urls
urlpatterns = [
    # path("task/create", CreateTaskView.as_view(), name=""),
    # path("task/list", ListTaskView.as_view(), name=""),
    # path("task", TaskView.as_view(), name=""),
    # path("task/delete", Dele.as_view(), name="")
    path("task/selected", TaskSelectedView.as_view(), name=""),
    path("task/checkoff", TaskCheckOffApiView.as_view(), name=""),
    path("task/timer", TaskTimerView.as_view(), name=""),
    path("dashboard/", DashboardAPIView.as_view(), name=""),
    # Timer
    path("timer/start", StartTimeView.as_view(), name="start_timer"),
    path("timer/update", UpdateTimeView.as_view(), name=""),
    path("timer/status", TimerStatus.as_view(), name=""),
    # Config
    path("configuration/", ConfigApiView.as_view(), name=""),
    path("configuration/update/", ConfigUpdateAPIView.as_view(), name=""),
    # Break
    path("break/create", CreateBreakView.as_view(), name=""),
    path("break/stop", PauseBreakView.as_view(), name=""),
    # Task
    path("task/template", TemplateAPI.as_view(), name=""),
    path("task/checkoff/reset", RemoveCheckOff.as_view()),
    # Dashboard
    path("dashboard/barchart", BarChartAPIView.as_view()),
    # re_path("", include(router.urls)),
        path('', include(router.urls)),
]
