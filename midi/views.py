# class preset
# contains  mod x, y settings 
# generate firmware of class "preset", flash firmware to either atmega 32u4, rp2040 or esp32 s3

from django.shortcuts import render, redirect
from .forms import UserForm
from .forms import KnobFormSet
from .models import Preset, Knob
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import FileResponse
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import KeypressChannelForm
# Create your views here.

def home(request):
    white_keys = [{'x': 20 + i * 58} for i in range(15)]
    black_keys = [{'x': 40 + i * 58} for i in [0,1,3,4,5,7,8,10,11,12]]
    return render(request, 'midi/home.html', {'hide_home_link': True})

@login_required(login_url='login')
def portal(request):
    user = request.user
    preset = request.GET.get('preset')
    presets = Preset.objects.filter(owner=user)
    preset_id = request.GET.get('preset')
    if preset_id:
        preset = presets.filter(id=preset_id).first()
    else:
        preset = presets.first()
    if preset:
        knobs = preset.knob_set.all()
    else:
        knobs = Knob.objects.none()
    firmware_path = None

    # for knob in knobs:
    #     temp = Knob.objects.create(
    #         preset = preset, 
    #         channel = , 
    #         cc = , 
    #         min = , 
    #         max = , 
    #         pin = ,
    #     )

    # preset = Preset.objects.create(
    #     owner = user,
    #     name = request.preset.preset_name, 
    #     keys_channel = request.Post.get('keys_channel'),
    #     number_of_knobs = knobs.count(),
    # )

    if request.method == 'POST':
        knob_formset = KnobFormSet(request.POST, queryset=Knob.objects.filter(preset=preset))
        midi_form = KeypressChannelForm(request.POST)
        if knob_formset.is_valid() and midi_form.is_valid():
            knob_formset.save()  # Save all knob settings for the preset
            preset.number_of_knobs = Knob.objects.filter(preset=preset).count()
            # Update the keypress channel
            preset.keys_channel = midi_form.cleaned_data['midi_channel']
            preset.save()
            # Improved firmware generation logic
            firmware_template = '''
// SweetBox SYNTHAGE Firmware
// Preset: {preset_name}
const int NUM_KNOBS = {num_knobs};
int knobChannels[NUM_KNOBS] = {{ {channels} }};
int knobCCs[NUM_KNOBS] = {{ {ccs} }};
int knobMins[NUM_KNOBS] = {{ {mins} }};
int knobMaxs[NUM_KNOBS] = {{ {maxs} }};
// ... rest of your firmware ...
'''
            knob_objs = Knob.objects.filter(preset=preset)
            firmware_content = firmware_template.format(
                preset_name=preset.name,
                num_knobs=knob_objs.count(),
                channels=', '.join(str(k.channel) for k in knob_objs),
                ccs=', '.join(str(k.CC) for k in knob_objs),
                mins=', '.join(str(k.min) for k in knob_objs),
                maxs=', '.join(str(k.max) for k in knob_objs),
            )
            firmware_dir = os.path.join(settings.BASE_DIR, 'generated_firmware')
            os.makedirs(firmware_dir, exist_ok=True)
            firmware_path = os.path.join(firmware_dir, f'firmware_preset_{preset.id}.ino')
            with open(firmware_path, 'w') as f:
                f.write(firmware_content)
            messages.success(request, 'Settings saved and firmware generated!')
            return redirect(request.path + f'?preset={preset.id}')
        else:
            # Errors will be shown in the template
            pass
    else:
        knob_formset = KnobFormSet(queryset=knobs, initial=[{'channel': 1, 'CC': 0, 'min': 0, 'max': 127, 'pin': 0}])
        midi_form = KeypressChannelForm(initial={'midi_channel': preset.keys_channel if preset else 1})

    download_url = None
    if firmware_path:
        download_url = f'/download_firmware/{preset.id}/'

    context = {
        'knob_formset': knob_formset,
        'preset': preset,
        'presets': presets,
        'download_url': download_url,
        'hide_portal_link': True,
        'midi_form': midi_form,
    }

    return render(request, 'midi/portal.html', context)

@login_required(login_url='/login/')
def download_firmware(request, preset_id):
    firmware_dir = os.path.join(settings.BASE_DIR, 'generated_firmware')
    firmware_path = os.path.join(firmware_dir, f'firmware_preset_{preset_id}.ino')
    if os.path.exists(firmware_path):
        return FileResponse(open(firmware_path, 'rb'), as_attachment=True, filename=f'firmware_preset_{preset_id}.ino')
    return redirect('/portal/')

@csrf_exempt
@login_required(login_url='/login/')
def create_preset(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        number_of_knobs = int(request.POST.get('number_of_knobs', 4))
        user = request.user
        preset = Preset.objects.create(owner=user, name=name, number_of_knobs=number_of_knobs)
        # Create default knobs for the preset
        for i in range(number_of_knobs):
            Knob.objects.create(preset=preset, channel=1, CC=24+i, min=0, max=127)
        messages.success(request, f'Preset "{name}" created!')
        return redirect(f'/portal/?preset={preset.id}')
    return redirect('/portal/')

def signUp(request):
    form = UserForm
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('/')


    context = {'form':form}
    return render(request, 'midi/login.html', context)

def login_view(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('/portal/')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('/portal/')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'page': page,
    }
    return render(request, 'midi/login.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('home')
