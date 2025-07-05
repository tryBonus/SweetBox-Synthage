from django import forms
from django.forms import ModelForm, BaseModelFormSet, ValidationError
from .models import Preset, Knob, Joystick, ModWheel, PitchWheel
from django.contrib.auth.models import User
from django.forms import modelformset_factory


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password', 
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }


class KnobForm(ModelForm):
    channel = forms.IntegerField(
        label='Channel', 
        min_value=1, 
        max_value=16,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-16'
        })
    )
    CC = forms.IntegerField(
        label='CC Number', 
        min_value=0, 
        max_value=127,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-127'
        })
    )
    min = forms.IntegerField(
        label='Minimum Value', 
        min_value=0, 
        max_value=127,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-127'
        })
    )
    max = forms.IntegerField(
        label='Maximum Value', 
        min_value=0, 
        max_value=127,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-127'
        })
    )
    pin = forms.IntegerField(
        label='Pin Number', 
        min_value=0, 
        max_value=99,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-99'
        })
    )
    
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
        channel = self.cleaned_data.get('channel')
        if channel is None:
            raise forms.ValidationError('Channel is required.')
        if not (1 <= channel <= 16):
            raise forms.ValidationError('Channel must be between 1 and 16.')
        return channel

    def clean_CC(self):
        cc = self.cleaned_data.get('CC')
        if cc is None:
            raise forms.ValidationError('CC Number is required.')
        if not (0 <= cc <= 127):
            raise forms.ValidationError('CC number must be between 0 and 127.')
        return cc

    def clean_min(self):
        min_value = self.cleaned_data.get('min')
        if min_value is None:
            raise forms.ValidationError('Minimum value is required.')
        if not (0 <= min_value <= 127):
            raise forms.ValidationError('Min value must be between 0 and 127.')
        return min_value

    def clean_max(self):
        max_value = self.cleaned_data.get('max')
        if max_value is None:
            raise forms.ValidationError('Maximum value is required.')
        if not (0 <= max_value <= 127):
            raise forms.ValidationError('Max value must be between 0 and 127.')
        return max_value

    def clean_pin(self):
        pin = self.cleaned_data.get('pin')
        if pin is None:
            raise forms.ValidationError('Pin number is required.')
        if not (0 <= pin <= 99):
            raise forms.ValidationError('Pin number must be between 0 and 99.')
        return pin

    def clean(self):
        cleaned_data = super().clean()
        min_value = cleaned_data.get('min')
        max_value = cleaned_data.get('max')
        
        if min_value is not None and max_value is not None and min_value > max_value:
            raise forms.ValidationError('Minimum value cannot be greater than maximum value.')
        
        return cleaned_data


class BaseKnobFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        seen_cc = set()
        seen_pin = set()
        non_empty_forms = 0
        
        for form in self.forms:
            if not hasattr(form, 'cleaned_data') or not form.cleaned_data:
                continue
            if form.cleaned_data.get('DELETE', False):
                continue
            
            # Count non-empty forms
            if any(form.cleaned_data.get(field) is not None for field in ['channel', 'CC', 'min', 'max', 'pin']):
                non_empty_forms += 1
            
            # Check for required fields
            required_fields = ['channel', 'CC', 'min', 'max', 'pin']
            for field in required_fields:
                if form.cleaned_data.get(field) is None:
                    raise ValidationError(f'All fields are required for each knob.')
            
            # Check for duplicate CC numbers
            cc = form.cleaned_data.get('CC')
            if cc in seen_cc:
                raise ValidationError(f'Duplicate CC Number {cc} detected. Each knob must have a unique CC Number.')
            seen_cc.add(cc)
            
            # Check for duplicate pin numbers
            pin = form.cleaned_data.get('pin')
            if pin in seen_pin:
                raise ValidationError(f'Duplicate Pin Number {pin} detected. Each knob must have a unique Pin Number.')
            seen_pin.add(pin)
        
        # Ensure at least one knob is configured
        if non_empty_forms == 0:
            raise ValidationError('At least one knob must be configured.')


KnobFormSet = modelformset_factory(
    Knob, 
    form=KnobForm, 
    formset=BaseKnobFormSet, 
    extra=0, 
    can_delete=True,
    validate_min=True,
    min_num=1,
    max_num=16
)


class KeypressChannelForm(forms.Form):
    midi_channel = forms.IntegerField(
        label='Keypress Channel', 
        min_value=1, 
        max_value=16,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-16'
        })
    )
    
    def clean_midi_channel(self):
        channel = self.cleaned_data.get('midi_channel')
        if channel is None:
            raise forms.ValidationError('MIDI channel is required.')
        if not (1 <= channel <= 16):
            raise forms.ValidationError('MIDI channel must be between 1 and 16.')
        return channel


class PresetForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter preset name'
        })
    )
    keys_channel = forms.IntegerField(
        min_value=1,
        max_value=16,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-16'
        })
    )
    number_of_knobs = forms.IntegerField(
        min_value=1,
        max_value=16,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1-16'
        })
    )
    
    class Meta:
        model = Preset
        fields = ['name', 'keys_channel', 'number_of_knobs']
        labels = {
            'name': 'Preset Name',
            'keys_channel': 'Keys Channel',
            'number_of_knobs': 'Number of Knobs',
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('Preset name is required.')
        return name.strip()
    
    def clean_keys_channel(self):
        channel = self.cleaned_data.get('keys_channel')
        if channel is None:
            raise forms.ValidationError('Keys channel is required.')
        if not (1 <= channel <= 16):
            raise forms.ValidationError('Keys channel must be between 1 and 16.')
        return channel
    
    def clean_number_of_knobs(self):
        knobs = self.cleaned_data.get('number_of_knobs')
        if knobs is None:
            raise forms.ValidationError('Number of knobs is required.')
        if not (1 <= knobs <= 16):
            raise forms.ValidationError('Number of knobs must be between 1 and 16.')
        return knobs