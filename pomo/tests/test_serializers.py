from django.test import TestCase
from ..models import Task,Configuration,Theme
# Create your tests here.
from ..serializers import TaskSerializer,ConfigurationSerializer,ThemeSerializer,BreakSerializer
from django.contrib.auth.models import User
# SERIALIZER TEST
class TestTaskSerializer(TestCase):
    def test_create(self):
        user = User.objects.create_user(username='testuser',password='testpassword')
        ser=  TaskSerializer(user=User.objects.first(),data={'title':'Complete','want_to_focus':1,'description':'Pomo Project'})
        if ser.is_valid():
            ser.save()
            task = Task.objects.first()
            self.assertEqual(task.title,'Complete')
        else:
            print('Error')
            
class TestThemeSerialzier(TestCase):
    def test_create(self):
        ser = ThemeSerializer(data={'short':'#aaaa','long':'#cbcd','pomodoro':'#edac'})
        if ser.is_valid():
            ser.save()
            theme =Theme.objects.first()
            self.assertEqual(theme.short,'#aaaa')
            self.assertEqual(theme.long,'#cbcd')
            self.assertEqual(theme.pomodoro,'#edac')


class TestConfigurationSerializer(TestCase):
    def test_create(self):
        user = User.objects.create_user(username='testuser',password='testpassword')
        theme = ThemeSerializer(data={'short':'#aaaa','long':'#cbcd','pomodoro':'#edac'})
        if theme.is_valid():
            theme.save()
            ser = ConfigurationSerializer(user=User.objects.first(),data={'theme':theme,'pomo_time':25,'short_break_time':5,'long_break_time':10})
            if ser.is_valid():
                ser.save()
                conf = Configuration.objects.first()
                self.assertEqual(conf.pomo_time,25)
                self.assertEqual(conf.short_break_time,5)
                self.assertEqual(conf.long_break_time,10)

class TestTaskSerializer(TestCase):
    def test_create(self):
        user = User.objects.create_user(username='testuser',password='testpassword')
        ser = TaskSerializer(data={'title':'Pomo project','description':'Complete this today','want_to_focus':3})
        if ser.is_valid():
            ser.save()
            task = Task.objects.first()
            self.assertEqual(task.title,'Pomo project')
            
# class TestBreakSerializer(TestCase):
#     def test_create(self):
#         user = User.objects.create_user(username='testuser',password='testpassword')
#         ser = BreakSerializer()