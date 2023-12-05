from rest_framework import serializers
from .models import Task,Timer,Paused,TaskSelected,Configuration,Theme
from .utils import parse_date
class PausedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paused
        fields = '__all__'  
class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields='__all__'
    # def validate_start_time(self,value):
    #     return parse_date(value)
    

class TimerDataSerializer(serializers.ModelSerializer):
    paused = PausedSerializer(many=True)
    class Meta:
        model = Timer
        fields='__all__'


        
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title','description','want_to_focus']
    # def save(self, **kwargs):
        
class TaskDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','title','description','want_to_focus']
        
class TaskSelectedSerializer(serializers.ModelSerializer):
    task = TaskDataSerializer()
    class Meta:
        model = TaskSelected
        fields= ['task']
        
class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'
class ConfigurationSerializer(serializers.ModelSerializer):
    theme = ThemeSerializer()
    class Meta:
        model = Configuration
        fields ='__all__'

