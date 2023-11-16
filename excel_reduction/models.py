from django.db import models

# Create your models here.

class ExcelFile(models.Model):
    file_data = models.FileField()
    uploaded_on = models.DateField(auto_created=True,null=True)
    def __str__(self):
        return self.file_data.name

class DeleteProfile(models.Model):
    name = models.CharField(max_length=100) # for which file
    columns = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    
    
# Add filter system for col and remove dates which are old - like adding rules and then add the same to profile