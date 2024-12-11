from django.shortcuts import get_object_or_404
from httpx import delete
from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework import viewsets
from rest_framework.response import Response
# from .serializers import *
from rest_framework import status
# from .utils import parse_datetime_with_timezone, time_left_in_seconds
from django.utils import timezone
from django.db import transaction

# from django.db.transaction import atomic
from .models import *
import datetime
# from .utils import check_if_any_timer_already_active
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

# right now working on guest user only

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def update(self, request):
        pass

    def create(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass
