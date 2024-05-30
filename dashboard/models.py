from ast import List
from typing import Any
from django.db import models
from django.forms import DateField

# Create your models here.

class CodeFile(models.Model):
    code = models.IntegerField()
    def __str__(self):
        return "{}".format(self.code)

class Activity(models.Model):
    name = models.CharField(max_length=200)
    code = models.IntegerField()
    code_file = models.ManyToManyField(CodeFile)

    def __str__(self) -> str:
        return self.name

class Agent(models.Model):
    code_agent = models.IntegerField()
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    activities = models.ManyToManyField(Activity)

    def __str__(self) -> str:
        return "{} {}".format(self.last_name, self.first_name)


class Flow(models.Model):
    start_date = models.DateField(verbose_name="Date début")
    end_date = models.DateField(verbose_name="Date fin")
    # timeline = models.IntegerField(verbose_name="Nombre de jours")
    activity = models.OneToOneField(
        Activity,
        on_delete =  models.CASCADE,
        primary_key = True,
    )
    workforce = models.IntegerField(verbose_name="Effectif")
    offered_calls = models.IntegerField(verbose_name="Offered Calls")
    dealed_calls = models.IntegerField(verbose_name="Appels traités")
    total_presence_time = models.IntegerField(verbose_name="Temps de présence/h")
    total_working_time = models.IntegerField(verbose_name="Temps de travail/h")
    total_waiting_time = models.IntegerField(verbose_name="Temps d'attente/h")
    waiting_time_rate = models.IntegerField(verbose_name="Pourcentage d'attente/h")
    total_pausing_time = models.IntegerField(verbose_name="Temps de pause/h")
    pausing_time_rate = models.IntegerField(verbose_name="Pourcentage de pause/h")
    total_production_time = models.IntegerField(verbose_name="Temps de production/h")
    total_calls_per_fte_per_day = models.IntegerField(verbose_name="Calls per FTE per day")
    occupancy_rate = models.IntegerField(verbose_name="Taux d'occupation")
    internal_shrinkage = models.IntegerField(verbose_name="Shrinkage interne")
    a_productivity = models.IntegerField(verbose_name="Productivité")
    paid_hours = models.IntegerField(verbose_name="Heures payées")
    external_shrinkage = models.IntegerField(verbose_name="Shrinkage externe")
    shrinkage = models.IntegerField(verbose_name="Shrinkage")
    b_productivity = models.IntegerField(verbose_name="Productivity")
    sl = models.IntegerField(verbose_name="SL")
    qs = models.IntegerField(verbose_name="QS")
    dma = models.IntegerField(verbose_name="DMA")
    dmc = models.IntegerField(verbose_name="DMC")
    dpt = models.IntegerField(verbose_name="DPT")
    dmt = models.IntegerField(verbose_name="DMT")


class LittleFlow(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    activity = models.OneToOneField(
        Activity,
        on_delete = models.CASCADE,
        primary_key = True,
    )
    offered_calls = models.IntegerField(verbose_name="Appels offerts")
    dealed_calls = models.IntegerField(verbose_name="Appels traités")
    dma = models.IntegerField(verbose_name="DMA")
    dmc = models.IntegerField(verbose_name="DMC")
    dmt = models.IntegerField(verbose_name="DMT")
    dpt = models.IntegerField(verbose_name="DPT")
    ivr = models.IntegerField(verbose_name="IVR")
    ignored = models.IntegerField(verbose_name="Ignorés")
    gived_up = models.IntegerField(verbose_name='Abandonnés')
    qs = models.IntegerField(verbose_name='QS')
    sl = models.IntegerField(verbose_name='SL')


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        # return "{}".format(self.file.split("/")[1])
        return "{}".format(self.file.name.split("/")[1])