from django.contrib import admin
from .models import Preset, Knob, Joystick, ModWheel, PitchWheel

# Register your models here.
admin.site.register(Preset)
admin.site.register(Knob)
admin.site.register(Joystick)
admin.site.register(ModWheel)
admin.site.register(PitchWheel)