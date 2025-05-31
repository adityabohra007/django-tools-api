from django.urls import path
from .views import upload_and_extract,uploaded_extracting,extraction_api,delete_column
urlpatterns = [
    path('home',upload_and_extract),
    path('extracting/<int:id>',uploaded_extracting,name='uploaded_extracting'),
    path("extraction_api/", extraction_api, name=""),
    path("extraction_api/delete/",delete_column,)
]

# Delete top null 