from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify


"""Модель представления нозологий"""
class Nosology(models.Model):

    idnosology = models.BigAutoField(primary_key=True)
    url = models.SlugField(max_length=128, unique=True)
    nosologyname = models.CharField('Nosology', max_length=128, blank=True, null=True)

    def __str__(self):
        return self.nosologyname

    class Meta:
        verbose_name = 'Nosology'
        verbose_name_plural = 'Nosologies'


"""Модель представления пациентов"""
class Patient(models.Model):

    iduser = models.BigAutoField(primary_key=True)
    url = models.SlugField(max_length=128, unique=False)
    username = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


"""Модель представления всех данных для нозологий"""
class Nosologydata(models.Model):

    iddata = models.BigAutoField(primary_key=True)
    idnosology = models.ForeignKey(Nosology, models.DO_NOTHING)
    value = models.CharField(max_length=45, blank=True, null=True)
    valuetype = models.CharField(max_length=45, blank=True, null=True)
    inpout = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = 'Nosologydata'
        verbose_name_plural = 'Nosologydata'


"""Модель представления всех наблюдений по нозологиям и пациентам"""
class Observer(models.Model):

    idobserver = models.BigAutoField(primary_key=True)
    idmodel = models.ForeignKey(Nosologydata, models.DO_NOTHING)
    iduser = models.ForeignKey(Patient, models.DO_NOTHING)
    val = models.CharField(db_column='Val', max_length=45, blank=True, null=True)
    cortege = models.IntegerField(db_column='Cortege', blank=True, null=True)

    def __str__(self):
        return str(self.iduser) + '_' + str(self.cortege) + '_' + str(self.idmodel)

    class Meta:
        verbose_name = 'Observer'
        verbose_name_plural = 'Observer'
        get_latest_by = 'cortege'
