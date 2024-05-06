from django import forms

from .models import Activity, UploadedFile


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        # fields = '__all__'
        fields = '__all__'
        # fields = ['code_file']
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['code_file'].widget.attrs['readonly'] = True


"""class FileUploadform(forms.Model):
    class Meta:
        model = UploadedFile
        file = forms.FileField()"""

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']