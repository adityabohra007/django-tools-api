from django.forms import Form,ModelForm
from .models import ExcelFile
class UploadFileForm(ModelForm):
    class Meta:
        model = ExcelFile
        fields = ['file_data']
        