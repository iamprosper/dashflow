from django.contrib import admin

from .forms import ActivityForm

from .models import Activity, Agent


class ActivityAdmin(admin.ModelAdmin):
    # change_form_template = "admin/dashboard/change_form.html"
    form = ActivityForm
    readonly_fields = ['code_file']

# Register your models here.
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Agent)