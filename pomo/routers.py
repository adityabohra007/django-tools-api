from .api import TaskViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"task", TaskViewset, basename="task")
urlpatterns = router.urls
