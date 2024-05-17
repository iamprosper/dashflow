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


class FilterFlow(forms.Form):
    # start_date = forms.DateField(label='Date début', widget=forms.DateInput(attrs={'type': 'date'}))
    # end_date = forms.DateField(label='Date fin', widget=forms.DateInput(attrs={'type': 'date'}))
    date = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'datepicker-here form-control',
                                                                        'placeholder': 'Sélectionnez la période',
                                                                        'id': 'minMaxExample',
                                                                        'data-date-format': 'dd/mm/yyyy',
                                                                        'data-language': 'en'}))
    activity = forms.ModelChoiceField(queryset=Activity.objects.all(), widget=forms.Select(attrs={'class': 'form-control',
                                                                                                  'aria-label': 'Activité',
                                                                                                  'id': 'activity'},
                                                                                                  ),
                                                                    empty_label="Selectionnez l'activité",
                                                                    to_field_name='code')
    # activity_choices = Activity.objects.all().values_list('name')
    # activity = forms.MultipleChoiceField(choices=activity_choices, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))