from rest_framework import serializers
from .models import Task,Timer,Paused
class PausedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paused
        fields = '__all__'  
class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields='__all__'

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
        
