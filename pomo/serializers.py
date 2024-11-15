from rest_framework import serializers
from rest_framework.fields import empty
from .models import *
from .utils import parse_date
class PausedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paused
        fields = '__all__'  
class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields='__all__'
    def __init__(self,user, instance=None, data=..., **kwargs):
        self.user=user
        super().__init__(instance, data, **kwargs)
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
        fields = '__all__'
    def __init__(self,user,instance=None, data=..., **kwargs):
        self.user= user
        super().__init__(instance, data, **kwargs)
    # def save(self, **kwargs):

class TaskCheckOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('check_off',)
        
class TaskDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','title','description','want_to_focus','check_off']
        
class TaskSelectedSerializer(serializers.ModelSerializer):
    task = TaskDataSerializer()
    class Meta:
        model = TaskSelected
        fields= ['task']
        
class TaskTimerSerializer(serializers.ModelSerializer):
    task = TaskDataSerializer()
    timer = TimerDataSerializer()
    class Meta:
        model = TaskTimer
        fields="__all__"
class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'
class ConfigurationSerializer(serializers.ModelSerializer):
    theme = ThemeSerializer()
    class Meta:
        model = Configuration
        fields ='__all__'
    # def update(self, instance, validated_data):
        # print(instance,validated_data,'update')
        # instance.theme.pomodoro = validated_data['theme']['pomodoro']
        # instance.theme.short_break = validated_data['theme']['short_break']
        # instance.theme.long_break = validated_data['theme']['long_break']
        # instance.theme.save()


        # return super().update(instance, validated_data)
class ConfigurationUpdateSerializer(serializers.ModelSerializer):
    # theme = ThemeSerializer()
    class Meta:
        model = Configuration
        exclude =['id','user','theme']

class ConfigurationFormSerializer(serializers.ModelSerializer):
    theme = ThemeSerializer()
    class Meta:
        model = Configuration
        exclude =['theme']


class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        fields=['id','start_time','end_time','break_type']
        
class TaskTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplateItem
        fields='__all__'
class TaskTemplateSerializer(serializers.ModelSerializer):
    # task = TaskTemplateItemSerializer(many=True)
    class Meta:
        model = TaskTemplate
        fields='__all__'
# class BarChartSerializer(serializers.ModelSerializer):
    