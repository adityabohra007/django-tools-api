from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Task)
admin.site.register(Timer)
admin.site.register(TaskSelected)
admin.site.register(TaskPosition)
admin.site.register(TaskTimer)
admin.site.register(Configuration)
admin.site.register(Theme)