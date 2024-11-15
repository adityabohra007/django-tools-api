from .api import TaskViewset, ConfigViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"task", TaskViewset, basename="task")
router.register(r"configuration", ConfigViewSet, basename="config")
urlpatterns = router.urls
