#!/usr/bin/python
#-*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from tools import *

weekdays_model = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']   

# used on all fields that need to have a forced max_length
# django doesnt do this validation by itself
# the value given to MaxLengthValidator should be same as max_length variable
from django.core.validators import MaxLengthValidator

import uuid

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When a a new user is created, create a corresponding UserProfile
    TODO: Create different profiles depending on if it's a stylist or a regular user
    """
    if created:
        UserProfile.objects.create(user=instance,
                                   temporary_profile_url= uuid.uuid4().hex, 
                                   profile_name = 'Namn Namnsson', 
                                   profile_phone_number = "0761234567",
                                   display_on_first_page = True,
                                   salon_name = 'Gunillas hårparadis',
                                   salon_city = 'Linköping',
                                   salon_adress = 'Musterivägen 12A',
                                   salon_phone_number = '013523812',
                                   zip_adress  = 38413,
                                   profile_text = 'Det här är en beskrivande text av vad salongen är och står för, samt annan intressant information')

        OpenHours.objects.create(user=instance)

        Service.objects.create(user = instance, 
                                length = 60, 
                                name = "Klippning",
                                price = 500, 
                                description = "Klipp ditt hår fint till sommaren", 
                                display_on_profile = True)


        Service.objects.create(user = instance, 
                                length = 105, 
                                name = "Hårfärgning",
                                price = 140, 
                                description = "Bli fin som en dräng med Pers intensiva hårfärg.", 
                                display_on_profile = True)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)
    profile_name = models.CharField("Mitt Namn*", max_length=40, blank=True)
    profile_phone_number = models.CharField("Personligt Telefonnummer", max_length=30, blank=True)

    display_on_first_page = models.BooleanField(editable=False)
    
    # max_length? less?
    profile_text = models.CharField("Om mig", max_length=500, blank=True)

    # TODO: add check if unique
    profile_url = models.CharField("Min Stylefinder hemsida*", max_length=15, blank=True, validators=[MaxLengthValidator(15)])
    # used to reach profile if no profile_url set
    temporary_profile_url = models.CharField(editable=False, unique=True, max_length=36)

    """
    TODO:
    fixa så email från huvudprofilen visas här
    fixa så twitter och facebook profil visas här, se styleseat
    """
    
    # salong
    salon_name = models.CharField("Salongens Namn", max_length=30, blank=True)
    salon_city = models.CharField("Stad", max_length=30, blank=True)
    salon_url = models.URLField("Salongens Hemsida", blank=True)
    salon_adress = models.CharField("Salongens Adress",max_length=30, blank=True)
    salon_phone_number = models.CharField("Salongens Telefonnummer", max_length=30, blank=True)
    
    # TODO: add validation https://docs.djangoproject.com/en/dev/ref/contrib/localflavor/#sweden-se
    zip_adress = models.IntegerField("Postnummer", max_length=6, blank=True, null=True)


    url_online_booking = models.URLField("Adress till online bokningssystem", blank=True)
    show_booking_url = models.BooleanField("Min salong har online-bokning", blank=True)
    
class Service(models.Model):
    buffer = generate_list_of_quarters(15, 420+15, format_minutes_to_pretty_format)
    TIME_CHOICES = tuple(buffer)


    length = models.IntegerField("Längd", choices=TIME_CHOICES,max_length=3)
    name = models.CharField("Namn (ex. Herrklippning)", max_length=20)
    price = models.IntegerField("Pris i kronor", max_length=6)
    
    # TODO: längd på desc? 
    description = models.CharField("Beskrivning", max_length=200, validators=[MaxLengthValidator(200)])
    display_on_profile = models.BooleanField("Visa på profil", blank=True)
    
    # user that has this service
    user = models.ForeignKey(User, editable=False)
    order = models.PositiveIntegerField(blank=True, editable=True, null=True)

    class Meta:
        # deliver the services sorted on the order field
        # needs to be here, or the services admin ui will break
        ordering = ['order']

class OpenHours(models.Model):
    
    time_list = generate_list_of_quarters()

    # Since Python tuples are immutable we need to use a list as a temporary buffer
    time_tuple = tuple(time_list)

    user = models.ForeignKey(User, editable=False)

    # 8:00 AM
    default_open_time = 480
    # 17:00 PM
    default_close_time = 1020

    # 12:00 - 13:00 PM
    default_lunch_open = 720
    default_lunch_close = 780

    # Instead of having duplicate code we generate the code dynamically and 
    # execute it. FIXME: This MIGHT be unsafe, so if any problem occurs in 
    # this model this is probably why.
    for day in weekdays_model:
        code = day + ' = models.IntegerField("", choices=time_tuple, default = ' + str(default_open_time) + ')'
        exec(code)

        code = day + '_closed = models.IntegerField("", choices=time_tuple, default = ' + str(default_close_time) + ')'
        exec(code)

        code = day + '_lunch = models.IntegerField("", choices=time_tuple, default = ' + str(default_lunch_open) + ')'
        exec(code)

        code = day + '_lunch_closed = models.IntegerField("", choices=time_tuple, default = ' + str(default_lunch_close) + ')'
        exec(code)
