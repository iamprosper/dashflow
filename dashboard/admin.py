from django.contrib import admin

from .forms import ActivityForm

from .models import Activity, Agent, CodeFile


# class ActivityAdmin(admin.ModelAdmin):
#     change_form_template = "admin/dashboard/change_form.html"
#     form = ActivityForm
#     readonly_fields = ['code_file']

# Register your models here.
admin.site.register(Activity)
admin.site.register(Agent)
admin.site.register(CodeFile)