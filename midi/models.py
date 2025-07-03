from django.db import models
from django.contrib.auth.models import User

class Preset(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    keys_channel = models.PositiveSmallIntegerField(default=1)
    number_of_knobs = models.PositiveSmallIntegerField(default=4)

    objects = models.Manager()

    def __str__(self):
        return self.name


# Class for knobs and sliders
class Knob(models.Model):
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE, null=True)
    channel = models.PositiveSmallIntegerField(null=True, default=1)
    CC = models.PositiveSmallIntegerField(default=24)
    min = models.IntegerField(default=0)
    max = models.IntegerField(default=127)
    pin = models.IntegerField(default=1)
    # knob_index =
    # pin = 

    objects = models.Manager()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)



class Joystick(models.Model):
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE, null=True)
    # x = 
    # y = 
    pass

class PitchWheel(models.Model):
    pass

class ModWheel(models.Model):
    # CC = 1
    pass
