from rest_framework import serializers
from .models import Todo, TodoList


class TodoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = "__all__"


class TodoListUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = ["title", "description"]


class TodoSerializer(serializers.ModelSerializer):
    todo_list = TodoListSerializer(many=True)

    class Meta:
        model = Todo
        fields = "__all__"


class CreateTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["title", "description", "custom_color_code", "category", "user"]

        def __init__(self, user, instance=None, data=..., **kwargs):
            self.user = user
            super().__init__(instance, data, **kwargs)


class TodoListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoList
        fields = ["title", "description"]
