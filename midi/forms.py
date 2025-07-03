from django import forms
from django.forms import ModelForm
from .models import Preset, Knob, Joystick, ModWheel, PitchWheel
from django.contrib.auth.models import User
from django.forms import modelformset_factory


class UserForm(ModelForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = [
            'email',
            'username',
            'password', 
        ]

class KnobForm(ModelForm):
    channel = forms.IntegerField(label='Channel', min_value=1, max_value=16)
    CC = forms.IntegerField(label='CC Number', min_value=0, max_value=127)
    min = forms.IntegerField(label='Minimum Value', min_value=0, max_value=127)
    max = forms.IntegerField(label='Maximum Value', min_value=0, max_value=127)
    pin = forms.IntegerField(label='Pin Number', min_value=0, max_value=99)
    class Meta:
        model = Knob
        fields = ['channel', 'CC', 'min', 'max', 'pin']
        labels = {
            'channel': 'Channel',
            'CC': 'CC Number',
            'min': 'Minimum Value',
            'max': 'Maximum Value',
            'pin': 'Pin Number',
        }

    def clean_channel(self):
        channel = self.cleaned_data['channel']
        if not (1 <= channel <= 16):
            raise forms.ValidationError('Channel must be between 1 and 16.')
        return channel

    def clean_CC(self):
        cc = self.cleaned_data['CC']
        if not (0 <= cc <= 127):
            raise forms.ValidationError('CC number must be between 0 and 127.')
        return cc

    def clean_min(self):
        min_value = self.cleaned_data['min']
        if not (0 <= min_value <= 127):
            raise forms.ValidationError('Min value must be between 0 and 127.')
        return min_value

    def clean_max(self):
        max_value = self.cleaned_data['max']
        if not (0 <= max_value <= 127):
            raise forms.ValidationError('Max value must be between 0 and 127.')
        return max_value

    def clean(self):
        cleaned_data = super().clean()
        min_value = cleaned_data.get('min')
        max_value = cleaned_data.get('max')
        if min_value is not None and max_value is not None and min_value > max_value:
            raise forms.ValidationError('Min value cannot be greater than max value.')
        return cleaned_data

KnobFormSet = modelformset_factory(Knob, form=KnobForm, extra=1, can_delete=True)

class KeypressChannelForm(forms.Form):
    midi_channel = forms.IntegerField(label='Keypress Channel', min_value=1, max_value=16)

class PresetForm(forms.ModelForm):
    class Meta:
        model = Preset
        fields = ['name', 'keys_channel', 'number_of_knobs']