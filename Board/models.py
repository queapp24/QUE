from django.db import models
from django.contrib.auth.models import User

class Driver(models.Model):
    DR_NAME = models.CharField(max_length=30, primary_key=True)
    DR_AREA = models.CharField(max_length=5, null=True, blank=True)
    DR_STAT = models.BooleanField(default=False)

    def __str__(self):
        return self.DR_NAME
    
    def status_update(self, status):
        Driver.objects.filter(pk=self.pk).update(DR_STAT=status)

    def area_update(self, area):
        Driver.objects.filter(pk=self.pk).update(DR_AREA=area)

class Arrival(models.Model):
    A_FTNA = models.CharField(max_length=20, primary_key=True)
    A_DRVR1 = models.ForeignKey(Driver, on_delete=models.DO_NOTHING, related_name='arr_main_related', db_column='DR_NAME', default=None, null=True, blank=True)
    A_CLSD = models.BooleanField(default=False)

    def __str__(self):
        return self.A_FTNA
    
    def driver_update_arr(self, DRVR):
        Arrival.objects.filter(pk=self.pk).update(A_DRVR1=DRVR)

    def close_arr(self, check):
        Arrival.objects.filter(pk=self.pk).update(A_CLSD=check)
    
class Departure(models.Model):
    D_FTND = models.CharField(max_length=20, primary_key=True)
    D_DRVR1 = models.ForeignKey(Driver, on_delete=models.DO_NOTHING, related_name='dep_main_related', db_column='DR_NAME', default=None, null=True, blank=True)
    D_CLSD = models.BooleanField(default=False)
    D_BAGSN = models.CharField(max_length=30, null=True, blank=True)
    D_ZONE = models.CharField(max_length=5, null=True, blank=True)
    D_SENT = models.BooleanField(default=False)

    def driver_update_dep(self, DRVR):
        Departure.objects.filter(pk=self.pk).update(D_DRVR1=DRVR)

    def close_dep(self, check):
        Departure.objects.filter(pk=self.pk).update(D_CLSD=check)

    def bags_closure_dep(self, bags_nbr):
        Departure.objects.filter(pk=self.pk).update(D_BAGSN=bags_nbr)

    def assign_zone_dep(self, zone):
        Departure.objects.filter(pk=self.pk).update(D_ZONE=zone)

    def sent_dep(self, sent):
        Departure.objects.filter(pk=self.pk).update(D_SENT=sent)

    def __str__(self):
        return self.D_FTND
    
class Hidden(models.Model):
    H_USER = models.ForeignKey(User, on_delete=models.CASCADE)
    H_FTND = models.ForeignKey(Departure, on_delete=models.CASCADE)
    H_HDDN = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.H_USER} - {self.H_FTND}"

class Rotation(models.Model):

# Arrival Info
    R_STAND = models.CharField(max_length=20, null=True, blank=True)
    R_ACREG = models.CharField(max_length=20, primary_key=True)
    R_FTNA = models.ForeignKey(Arrival, on_delete=models.DO_NOTHING, related_name='main_related', db_column='A_FTNA', default=None, null=True, blank=True)
    R_APTA = models.CharField(max_length=20, null=True, blank=True)
    R_STA = models.TimeField(null=True, blank=True)
    R_ETA = models.TimeField(null=True, blank=True)
    R_NA = models.CharField(max_length=100, null=True, blank=True)
# General Info
    R_RMPAG = models.CharField(max_length=20, null=True, blank=True)
# Departure Info
    R_FTND = models.ForeignKey(Departure, on_delete=models.DO_NOTHING, related_name='main_related', db_column='D_FTND', default=None, null=True, blank=True)
    R_APTD = models.CharField(max_length=20, null=True, blank=True)
    R_STD = models.TimeField(null=True, blank=True)
    R_ETD = models.TimeField(null=True, blank=True)
    R_SLT = models.TimeField(null=True, blank=True)
    R_ND = models.CharField(max_length=100, null=True, blank=True)
# Operational Info
    R_AOG = models.BooleanField(default=False)
    R_OOT = models.TimeField(null=True, blank=True)
    R_IOT = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.R_ACREG
