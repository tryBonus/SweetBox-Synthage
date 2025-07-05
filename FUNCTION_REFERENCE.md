# SweetBoxSYNTHAGE Function Reference

## Overview

This document provides detailed technical specifications for all functions, methods, and components in the SweetBoxSYNTHAGE system.

## Table of Contents

1. [View Functions](#view-functions)
2. [Model Methods](#model-methods)
3. [Form Methods](#form-methods)
4. [Utility Functions](#utility-functions)
5. [Template Functions](#template-functions)

---

## View Functions

### Authentication Views

#### `signUp(request)`
**File:** `midi/views.py:220`
**Purpose:** Handles user registration
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse
**HTTP Methods:** GET, POST
**Authentication:** Not required
**Template:** `midi/login_register.html`

**Function Signature:**
```python
def signUp(request):
    form = UserForm
    page = 'signup'
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid:
            form.save()
            create_default_preset(request.user)
            return redirect('login')
    
    context = {
        'form': form,
        'page': page,
    }
    return render(request, 'midi/login_register.html', context)
```

**POST Parameters:**
- `username`: String
- `email`: String
- `password`: String

**Context Variables:**
- `form`: UserForm instance
- `page`: String ('signup')

#### `login_view(request)`
**File:** `midi/views.py:237`
**Purpose:** Handles user authentication
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse
**HTTP Methods:** GET, POST
**Authentication:** Not required
**Template:** `midi/login_register.html`

**Function Signature:**
```python
def login_view(request):
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'page': page,
    }
    return render(request, 'midi/login_register.html', context)
```

**POST Parameters:**
- `username`: String
- `password`: String

**Context Variables:**
- `form`: AuthenticationForm instance
- `page`: String ('login')

#### `logout_view(request)`
**File:** `midi/views.py:260`
**Purpose:** Logs out the current user
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse (redirect)
**HTTP Methods:** GET
**Authentication:** Not required

**Function Signature:**
```python
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('home')
```

### Main Application Views

#### `home(request)`
**File:** `midi/views.py:30`
**Purpose:** Renders the home page
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse
**HTTP Methods:** GET
**Authentication:** Not required
**Template:** `midi/home.html`

**Function Signature:**
```python
def home(request):
    user = request.user
    if user.is_authenticated:
        create_default_preset(user)
    context = {
        'hide_home_link': True,
    }   
    return render(request, 'midi/home.html', context)
```

**Context Variables:**
- `hide_home_link`: Boolean (True)

#### `dashboard(request)`
**File:** `midi/views.py:268`
**Purpose:** Displays user's preset dashboard
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse
**HTTP Methods:** GET
**Authentication:** Required (`@login_required`)
**Template:** `midi/dashboard.html`

**Function Signature:**
```python
@login_required(login_url='login')
def dashboard(request):
    user = request.user
    presets = Preset.objects.filter(owner=user)
    preset_count = presets.count()

    context = {
        'hide_dashboard_link': True,
        'presets': presets,
        'preset_count': preset_count,
    }   
    return render(request, 'midi/dashboard.html', context)
```

**Context Variables:**
- `hide_dashboard_link`: Boolean (True)
- `presets`: QuerySet[Preset]
- `preset_count`: Integer

#### `portal(request)`
**File:** `midi/views.py:40`
**Purpose:** Main preset configuration interface
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse
**HTTP Methods:** GET, POST
**Authentication:** Required (`@login_required`)
**Template:** `midi/portal.html`

**Function Signature:**
```python
@login_required(login_url='login')
def portal(request):
    user = request.user
    presets = Preset.objects.filter(owner=user).order_by('-updated')
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
    knob_queryset = Knob.objects.filter(preset=preset)
    
    # ... form processing logic ...
```

**GET Parameters:**
- `preset`: Integer (optional) - Preset ID

**POST Parameters:**
- `preset_name`: String
- `midi_channel`: Integer (1-16)
- Knob formset fields

**Context Variables:**
- `knob_formset`: KnobFormSet instance
- `preset`: Preset object
- `presets`: QuerySet[Preset]
- `download_url`: String (optional)
- `hide_portal_link`: Boolean (True)
- `midi_form`: KeypressChannelForm instance

### CRUD Operations

#### `create_preset(request)`
**File:** `midi/views.py:142`
**Purpose:** Creates a new preset
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse (redirect)
**HTTP Methods:** POST
**Authentication:** Required (`@login_required`)
**CSRF:** Exempt (`@csrf_exempt`)

**Function Signature:**
```python
@csrf_exempt
@login_required(login_url='/login/')
def create_preset(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        keys_channel = int(request.POST.get('keys_channel', 1))
        number_of_knobs = int(request.POST.get('number_of_knobs', 4))
        user = request.user

        preset = Preset.objects.create(
            owner=user,
            name=name,
            keys_channel=keys_channel,
            number_of_knobs=number_of_knobs,
        )
        
        for i in range(preset.number_of_knobs):
            knob = Knob.objects.create(
                preset=preset,
                channel=1,
                CC=i,
                min=0,
                max=127,
                pin=i
            )

        messages.success(request, f'Preset "{name}" created successfully!')
        return redirect('dashboard')
    return redirect('dashboard')
```

**POST Parameters:**
- `name`: String (required)
- `keys_channel`: Integer (1-16, default: 1)
- `number_of_knobs`: Integer (1-16, default: 4)

#### `delete_preset(request, pk)`
**File:** `midi/views.py:171`
**Purpose:** Deletes a preset with confirmation
**Parameters:**
- `request`: HttpRequest object
- `pk`: String - Preset ID
**Returns:** HttpResponse
**HTTP Methods:** GET, POST
**Authentication:** Required (`@login_required`)
**Template:** `midi/delete.html`

**Function Signature:**
```python
@login_required(login_url='login')
def delete_preset(request, pk):
    preset = Preset.objects.get(id=pk)
    obj = preset.name

    if preset.owner != request.user:
        return HttpResponse('You are not allowed to be here!!', content_type='text/plain')

    if request.method == 'POST':
        preset.delete()
        return redirect('dashboard')

    context = {
        'obj': obj,
        'preset': preset,
    }
    return render(request, 'midi/delete.html', context)
```

**URL Parameters:**
- `pk`: String - Preset ID

**Context Variables:**
- `obj`: String - Preset name
- `preset`: Preset object

### Firmware Operations

#### `download_firmware(request, preset_id)`
**File:** `midi/views.py:133`
**Purpose:** Downloads generated firmware file
**Parameters:**
- `request`: HttpRequest object
- `preset_id`: Integer - Preset ID
**Returns:** FileResponse or HttpResponse (redirect)
**HTTP Methods:** GET
**Authentication:** Required (`@login_required`)

**Function Signature:**
```python
@login_required(login_url='/login/')
def download_firmware(request, preset_id):
    firmware_dir = os.path.join(settings.BASE_DIR, 'generated_firmware')
    firmware_path = os.path.join(firmware_dir, f'firmware_preset_{preset_id}.ino')
    
    if os.path.exists(firmware_path):
        return FileResponse(
            open(firmware_path, 'rb'), 
            as_attachment=True, 
            filename=f'firmware_preset_{preset_id}.ino'
        )
    return redirect(reverse('portal'))
```

**URL Parameters:**
- `preset_id`: Integer - Preset ID

**Return Values:**
- Success: FileResponse (firmware file)
- Error: HttpResponse (redirect to portal)

#### `generate_firmware(request)`
**File:** `midi/views.py:99`
**Purpose:** Generates firmware file for a preset
**Parameters:**
- `request`: HttpRequest object
**Returns:** HttpResponse (redirect)
**HTTP Methods:** GET
**Authentication:** Not specified

**Function Signature:**
```python
def generate_firmware(request):
    preset = Preset.objects.get(id=1)
    
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
    return redirect(f"{reverse('portal')}?preset={preset.id}")
```

### Utility Functions

#### `create_default_preset(user)`
**File:** `midi/views.py:18`
**Purpose:** Creates a default preset for new users
**Parameters:**
- `user`: User object
**Returns:** None
**Side Effects:** Creates Preset and Knob objects

**Function Signature:**
```python
def create_default_preset(user):
    if (Preset.objects.filter(owner=user).count() < 1) or (Preset.objects.filter(name='Default').count() < 1):
        preset = Preset.objects.create(
            owner=user,
            name='Default',
            keys_channel=1,
            number_of_knobs=4,
        )
        for i in range(preset.number_of_knobs):
            knob = Knob.objects.create(
                preset=preset,
                CC=i,
                pin=i,
            )
```

**Conditions:**
- Creates preset if user has no presets OR no "Default" preset exists
- Creates default knobs with CC and pin values 0-3

---

## Model Methods

### Preset Model Methods

#### `Preset.__str__(self)`
**File:** `midi/models.py:16`
**Purpose:** String representation of preset
**Parameters:**
- `self`: Preset instance
**Returns:** String (preset name)

**Function Signature:**
```python
def __str__(self):
    return self.name
```

### Knob Model Methods

#### `Knob.objects` (Manager)
**File:** `midi/models.py:30`
**Purpose:** Default model manager
**Type:** Django Manager

**Usage Examples:**
```python
# Get all knobs for a preset
knobs = Knob.objects.filter(preset=preset)

# Get knob by ID
knob = Knob.objects.get(id=knob_id)

# Create new knob
knob = Knob.objects.create(
    preset=preset,
    channel=1,
    CC=24,
    min=0,
    max=127,
    pin=0
)
```

---

## Form Methods

### UserForm Methods

#### `UserForm.save(commit=True)`
**File:** `midi/forms.py` (ModelForm)
**Purpose:** Saves user form data
**Parameters:**
- `commit`: Boolean (default: True)
**Returns:** User instance

### KnobForm Validation Methods

#### `KnobForm.clean_channel(self)`
**File:** `midi/forms.py:65`
**Purpose:** Validates channel field
**Parameters:**
- `self`: KnobForm instance
**Returns:** Integer (validated channel)
**Raises:** ValidationError

**Function Signature:**
```python
def clean_channel(self):
    channel = self.cleaned_data.get('channel')
    if channel is None:
        raise forms.ValidationError('Channel is required.')
    if not (1 <= channel <= 16):
        raise forms.ValidationError('Channel must be between 1 and 16.')
    return channel
```

#### `KnobForm.clean_CC(self)`
**File:** `midi/forms.py:73`
**Purpose:** Validates CC field
**Parameters:**
- `self`: KnobForm instance
**Returns:** Integer (validated CC number)
**Raises:** ValidationError

**Function Signature:**
```python
def clean_CC(self):
    cc = self.cleaned_data.get('CC')
    if cc is None:
        raise forms.ValidationError('CC Number is required.')
    if not (0 <= cc <= 127):
        raise forms.ValidationError('CC number must be between 0 and 127.')
    return cc
```

#### `KnobForm.clean_min(self)`
**File:** `midi/forms.py:81`
**Purpose:** Validates min field
**Parameters:**
- `self`: KnobForm instance
**Returns:** Integer (validated min value)
**Raises:** ValidationError

#### `KnobForm.clean_max(self)`
**File:** `midi/forms.py:89`
**Purpose:** Validates max field
**Parameters:**
- `self`: KnobForm instance
**Returns:** Integer (validated max value)
**Raises:** ValidationError

#### `KnobForm.clean_pin(self)`
**File:** `midi/forms.py:97`
**Purpose:** Validates pin field
**Parameters:**
- `self`: KnobForm instance
**Returns:** Integer (validated pin number)
**Raises:** ValidationError

#### `KnobForm.clean(self)`
**File:** `midi/forms.py:105`
**Purpose:** Cross-field validation
**Parameters:**
- `self`: KnobForm instance
**Returns:** Dictionary (cleaned data)

### BaseKnobFormSet Methods

#### `BaseKnobFormSet.clean(self)`
**File:** `midi/forms.py:113`
**Purpose:** Validates entire formset
**Parameters:**
- `self`: BaseKnobFormSet instance
**Returns:** None
**Raises:** ValidationError

**Function Signature:**
```python
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
```

**Validation Rules:**
- At least one knob required
- All fields required for each knob
- Unique CC numbers across all knobs
- Unique pin numbers across all knobs

### KeypressChannelForm Methods

#### `KeypressChannelForm.clean_midi_channel(self)`
**File:** `midi/forms.py:182`
**Purpose:** Validates MIDI channel field
**Parameters:**
- `self`: KeypressChannelForm instance
**Returns:** Integer (validated channel)
**Raises:** ValidationError

### PresetForm Methods

#### `PresetForm.clean_name(self)`
**File:** `midi/forms.py:213`
**Purpose:** Validates preset name field
**Parameters:**
- `self`: PresetForm instance
**Returns:** String (validated name)
**Raises:** ValidationError

#### `PresetForm.clean_keys_channel(self)`
**File:** `midi/forms.py:220`
**Purpose:** Validates keys channel field
**Parameters:**
- `self`: PresetForm instance
**Returns:** Integer (validated channel)
**Raises:** ValidationError

#### `PresetForm.clean_number_of_knobs(self)`
**File:** `midi/forms.py:229`
**Purpose:** Validates number of knobs field
**Parameters:**
- `self`: PresetForm instance
**Returns:** Integer (validated knob count)
**Raises:** ValidationError

---

## Template Functions

### Context Processors

The application uses standard Django context processors with custom context variables:

#### Common Context Variables
- `hide_home_link`: Boolean - Controls home link visibility
- `hide_dashboard_link`: Boolean - Controls dashboard link visibility
- `hide_portal_link`: Boolean - Controls portal link visibility

### Template Tags

The application uses standard Django template tags with form rendering:

#### Form Rendering
- `{{ form.field }}`: Renders form field
- `{{ form.field.errors }}`: Renders field errors
- `{{ form.non_field_errors }}`: Renders form-level errors

#### Formset Rendering
- `{{ formset.management_form }}`: Renders formset management form
- `{{ formset.non_form_errors }}`: Renders formset-level errors

---

## Error Handling Patterns

### View Error Handling

#### Common Error Patterns
```python
# Object not found
try:
    preset = Preset.objects.get(id=preset_id, owner=request.user)
except Preset.DoesNotExist:
    messages.error(request, 'Preset not found')
    return redirect('dashboard')

# Permission denied
if preset.owner != request.user:
    return HttpResponse('You are not allowed to be here!!', content_type='text/plain')

# Form validation
if form.is_valid():
    # Process form
    pass
else:
    # Handle errors
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f'{field}: {error}')
```

### Form Error Handling

#### Validation Error Patterns
```python
# Field validation
def clean_field(self):
    value = self.cleaned_data.get('field')
    if value is None:
        raise forms.ValidationError('Field is required.')
    if not (min_val <= value <= max_val):
        raise forms.ValidationError(f'Value must be between {min_val} and {max_val}.')
    return value

# Cross-field validation
def clean(self):
    cleaned_data = super().clean()
    # Validation logic
    return cleaned_data
```

---

## Performance Considerations

### Database Queries

#### Optimized Query Patterns
```python
# Prefetch related objects
presets = Preset.objects.filter(owner=user).prefetch_related('knob_set')

# Use select_related for foreign keys
knobs = Knob.objects.select_related('preset').filter(preset__owner=user)

# Order by for consistent results
presets = Preset.objects.filter(owner=user).order_by('-updated')
```

### File Operations

#### Firmware Generation
```python
# Create directory if needed
os.makedirs(firmware_dir, exist_ok=True)

# Safe file writing
with open(firmware_path, 'w') as f:
    f.write(firmware_content)
```

---

This function reference provides complete technical specifications for all functions in the SweetBoxSYNTHAGE system. Use this document for detailed implementation guidance and API integration.