# SweetBoxSYNTHAGE API Documentation

## Overview

SweetBoxSYNTHAGE is a Django-based web application for configuring MIDI controllers and generating firmware for various microcontrollers. The system allows users to create presets for MIDI controllers with custom knob configurations and automatically generate corresponding Arduino firmware.

## Table of Contents

1. [Authentication APIs](#authentication-apis)
2. [Preset Management APIs](#preset-management-apis)
3. [Portal Configuration APIs](#portal-configuration-apis)
4. [Firmware Generation APIs](#firmware-generation-apis)
5. [Models Reference](#models-reference)
6. [Forms Reference](#forms-reference)
7. [Firmware Components](#firmware-components)
8. [Usage Examples](#usage-examples)

---

## Authentication APIs

### 1. User Registration

**Endpoint:** `POST /sign-up/`
**View:** `signUp`
**Template:** `midi/login_register.html`

Creates a new user account and automatically generates a default preset.

**Parameters:**
- `username`: String, required
- `email`: String, required
- `password`: String, required

**Example:**
```html
<!-- Form submission -->
<form method="post" action="/sign-up/">
    {% csrf_token %}
    <input type="text" name="username" placeholder="Username" required>
    <input type="email" name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Sign Up</button>
</form>
```

**Response:**
- Success: Redirects to `/login/`
- Error: Returns form with validation errors

### 2. User Login

**Endpoint:** `POST /login/`
**View:** `login_view`
**Template:** `midi/login_register.html`

Authenticates user and creates session.

**Parameters:**
- `username`: String, required
- `password`: String, required

**Example:**
```html
<!-- Form submission -->
<form method="post" action="/login/">
    {% csrf_token %}
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>
```

**Response:**
- Success: Redirects to `/dashboard/`
- Error: Returns form with error messages

### 3. User Logout

**Endpoint:** `GET /logout/`
**View:** `logout_view`
**Authentication:** Required

Logs out the current user and destroys session.

**Example:**
```html
<a href="/logout/">Logout</a>
```

**Response:**
- Success: Redirects to `/` (home page)

---

## Preset Management APIs

### 1. Dashboard

**Endpoint:** `GET /dashboard/`
**View:** `dashboard`
**Template:** `midi/dashboard.html`
**Authentication:** Required

Displays all presets owned by the current user.

**Response Data:**
```python
{
    'presets': QuerySet[Preset],  # All user presets
    'preset_count': int,          # Total number of presets
    'hide_dashboard_link': True   # Navigation helper
}
```

**Example Usage:**
```html
<!-- Display presets -->
{% for preset in presets %}
    <div class="preset-item">
        <h3>{{ preset.name }}</h3>
        <p>Channel: {{ preset.keys_channel }}</p>
        <p>Knobs: {{ preset.number_of_knobs }}</p>
        <p>Updated: {{ preset.updated }}</p>
        <a href="/preset/?preset={{ preset.id }}">Configure</a>
        <a href="/delete_preset/{{ preset.id }}/">Delete</a>
    </div>
{% endfor %}
```

### 2. Create Preset

**Endpoint:** `POST /create_preset/`
**View:** `create_preset`
**Authentication:** Required

Creates a new preset with specified configuration.

**Parameters:**
- `name`: String, required - Preset name
- `keys_channel`: Integer, 1-16 - MIDI channel for keys
- `number_of_knobs`: Integer, 1-16 - Number of knobs to create

**Example:**
```html
<form method="post" action="/create_preset/">
    {% csrf_token %}
    <input type="text" name="name" placeholder="Preset Name" required>
    <input type="number" name="keys_channel" min="1" max="16" value="1" required>
    <input type="number" name="number_of_knobs" min="1" max="16" value="4" required>
    <button type="submit">Create Preset</button>
</form>
```

**Response:**
- Success: Redirects to `/dashboard/` with success message
- Error: Redirects to `/dashboard/` with error message

### 3. Delete Preset

**Endpoint:** `GET|POST /delete_preset/<int:pk>/`
**View:** `delete_preset`
**Template:** `midi/delete.html`
**Authentication:** Required

Displays confirmation page (GET) or deletes preset (POST).

**Parameters:**
- `pk`: Integer, required - Preset ID in URL

**Example:**
```html
<!-- Confirmation page -->
<form method="post">
    {% csrf_token %}
    <h2>Are you sure you want to delete "{{ preset.name }}"?</h2>
    <button type="submit">Yes, Delete</button>
    <a href="/dashboard/">Cancel</a>
</form>
```

**Response:**
- GET: Shows confirmation page
- POST Success: Redirects to `/dashboard/`
- POST Error: Returns 403 if user doesn't own preset

---

## Portal Configuration APIs

### 1. Portal (Main Configuration)

**Endpoint:** `GET|POST /preset/`
**View:** `portal`
**Template:** `midi/portal.html`
**Authentication:** Required

Main interface for configuring presets and knobs.

**Query Parameters:**
- `preset`: Integer, optional - Preset ID to configure

**GET Response Data:**
```python
{
    'knob_formset': KnobFormSet,        # Form for knob configuration
    'preset': Preset,                   # Current preset object
    'presets': QuerySet[Preset],        # All user presets
    'download_url': str,                # Firmware download URL
    'hide_portal_link': True,           # Navigation helper
    'midi_form': KeypressChannelForm,   # MIDI channel form
}
```

**POST Parameters:**
- `preset_name`: String - New preset name
- `midi_channel`: Integer, 1-16 - MIDI channel for keys
- Knob formset data (see KnobFormSet section)

**Example Usage:**
```html
<!-- Configure preset -->
<form method="post">
    {% csrf_token %}
    
    <!-- Preset name -->
    <input type="text" name="preset_name" value="{{ preset.name }}" required>
    
    <!-- MIDI channel -->
    {{ midi_form.midi_channel }}
    
    <!-- Knob configuration -->
    {{ knob_formset.management_form }}
    {% for form in knob_formset %}
        <div class="knob-form">
            {{ form.channel }}
            {{ form.CC }}
            {{ form.min }}
            {{ form.max }}
            {{ form.pin }}
            {{ form.DELETE }}
        </div>
    {% endfor %}
    
    <button type="submit">Save Configuration</button>
</form>
```

---

## Firmware Generation APIs

### 1. Download Firmware

**Endpoint:** `GET /download_firmware/<int:preset_id>/`
**View:** `download_firmware`
**Authentication:** Required

Downloads generated firmware file for a specific preset.

**Parameters:**
- `preset_id`: Integer, required - Preset ID in URL

**Response:**
- Success: File download (.ino file)
- Error: Redirects to `/preset/`

**Example:**
```html
<a href="/download_firmware/{{ preset.id }}/" download>
    Download Firmware
</a>
```

### 2. Generate Firmware (Internal)

**Function:** `generate_firmware`
**View:** `generate_firmware`

Generates Arduino firmware based on preset configuration.

**Generated Firmware Structure:**
```cpp
// SweetBox SYNTHAGE Firmware
// Preset: {preset_name}
const int NUM_KNOBS = {num_knobs};
int knobChannels[NUM_KNOBS] = { {channels} };
int knobCCs[NUM_KNOBS] = { {ccs} };
int knobMins[NUM_KNOBS] = { {mins} };
int knobMaxs[NUM_KNOBS] = { {maxs} };
// ... rest of firmware ...
```

---

## Models Reference

### 1. Preset Model

**File:** `midi/models.py`

Stores MIDI controller preset configurations.

**Fields:**
- `id`: AutoField, Primary Key
- `owner`: ForeignKey to User, CASCADE delete
- `name`: CharField, max_length=200
- `keys_channel`: PositiveSmallIntegerField, default=1
- `number_of_knobs`: PositiveSmallIntegerField, default=4
- `created`: DateTimeField, auto_now_add=True
- `updated`: DateTimeField, auto_now=True

**Methods:**
- `__str__()`: Returns preset name

**Example Usage:**
```python
from midi.models import Preset

# Create preset
preset = Preset.objects.create(
    owner=request.user,
    name="My Preset",
    keys_channel=1,
    number_of_knobs=4
)

# Query presets
user_presets = Preset.objects.filter(owner=request.user)
recent_presets = Preset.objects.filter(owner=request.user).order_by('-updated')
```

### 2. Knob Model

**File:** `midi/models.py`

Stores individual knob/slider configurations for presets.

**Fields:**
- `id`: AutoField, Primary Key
- `preset`: ForeignKey to Preset, CASCADE delete
- `channel`: PositiveSmallIntegerField, default=1
- `CC`: PositiveSmallIntegerField, default=24
- `min`: IntegerField, default=0
- `max`: IntegerField, default=127
- `pin`: IntegerField, default=0

**Relationships:**
- `preset.knob_set.all()`: Get all knobs for a preset

**Example Usage:**
```python
from midi.models import Knob

# Create knob
knob = Knob.objects.create(
    preset=preset,
    channel=1,
    CC=24,
    min=0,
    max=127,
    pin=0
)

# Query knobs
preset_knobs = Knob.objects.filter(preset=preset)
```

### 3. Future Models (Partially Implemented)

**Joystick Model:**
- `preset`: ForeignKey to Preset

**PitchWheel Model:**
- Not yet implemented

**ModWheel Model:**
- Not yet implemented

---

## Forms Reference

### 1. UserForm

**File:** `midi/forms.py`

User registration form.

**Fields:**
- `email`: EmailField
- `username`: CharField
- `password`: CharField with PasswordInput widget

**Example Usage:**
```python
from midi.forms import UserForm

form = UserForm(request.POST)
if form.is_valid():
    user = form.save()
```

### 2. KnobForm

**File:** `midi/forms.py`

Individual knob configuration form.

**Fields:**
- `channel`: IntegerField, range 1-16
- `CC`: IntegerField, range 0-127
- `min`: IntegerField, range 0-127
- `max`: IntegerField, range 0-127
- `pin`: IntegerField, range 0-99

**Validation:**
- All fields required
- Channel: 1-16
- CC: 0-127
- Min/Max: 0-127
- Pin: 0-99

**Example Usage:**
```python
from midi.forms import KnobForm

form = KnobForm(data={
    'channel': 1,
    'CC': 24,
    'min': 0,
    'max': 127,
    'pin': 0
})
```

### 3. KnobFormSet

**File:** `midi/forms.py`

Formset for managing multiple knobs simultaneously.

**Configuration:**
- `extra=0`: No extra forms
- `can_delete=True`: Allow deletion
- `min_num=1`: Minimum 1 knob
- `max_num=16`: Maximum 16 knobs

**Validation:**
- At least one knob required
- Unique CC numbers
- Unique pin numbers
- All required fields present

**Example Usage:**
```python
from midi.forms import KnobFormSet

# Initialize with queryset
formset = KnobFormSet(queryset=Knob.objects.filter(preset=preset))

# Process POST data
if request.method == 'POST':
    formset = KnobFormSet(request.POST, queryset=knob_queryset)
    if formset.is_valid():
        instances = formset.save(commit=False)
        for knob in instances:
            knob.preset = preset
            knob.save()
        formset.save_m2m()
```

### 4. KeypressChannelForm

**File:** `midi/forms.py`

Form for configuring MIDI channel for key presses.

**Fields:**
- `midi_channel`: IntegerField, range 1-16

**Example Usage:**
```python
from midi.forms import KeypressChannelForm

form = KeypressChannelForm(data={'midi_channel': 1})
if form.is_valid():
    channel = form.cleaned_data['midi_channel']
```

### 5. PresetForm

**File:** `midi/forms.py`

Form for creating/editing presets.

**Fields:**
- `name`: CharField, max_length=200
- `keys_channel`: IntegerField, range 1-16
- `number_of_knobs`: IntegerField, range 1-16

**Example Usage:**
```python
from midi.forms import PresetForm

form = PresetForm(data={
    'name': 'My Preset',
    'keys_channel': 1,
    'number_of_knobs': 4
})
```

---

## Firmware Components

### Supported Microcontrollers

1. **ATMEGA32U4** - Arduino Leonardo/Micro compatible
2. **ESP32_USB** - ESP32 with USB support
3. **RP2040** - Raspberry Pi Pico compatible

### Firmware Structure

Each microcontroller has a complete firmware template in:
- `midi/firmware/ATMEGA32U4/completebuild.ino`
- `midi/firmware/ESP32_USB/completebuild.ino`
- `midi/firmware/RP2040/completebuild.ino`

### Generated Firmware

The system generates custom firmware files in `generated_firmware/` directory with the following naming convention:
- `firmware_preset_{preset_id}.ino`

### Firmware Generation Process

1. User configures preset and knobs
2. System generates firmware code with preset-specific parameters
3. Firmware includes:
   - Number of knobs
   - MIDI channels for each knob
   - CC numbers for each knob
   - Min/max values for each knob
   - Pin assignments

---

## Usage Examples

### Complete Workflow Example

```python
# 1. Create a new preset
preset = Preset.objects.create(
    owner=request.user,
    name="Bass Synthesizer",
    keys_channel=1,
    number_of_knobs=4
)

# 2. Configure knobs
knobs_config = [
    {'channel': 1, 'CC': 74, 'min': 0, 'max': 127, 'pin': 0},  # Filter Cutoff
    {'channel': 1, 'CC': 71, 'min': 0, 'max': 127, 'pin': 1},  # Resonance
    {'channel': 1, 'CC': 73, 'min': 0, 'max': 127, 'pin': 2},  # Attack
    {'channel': 1, 'CC': 72, 'min': 0, 'max': 127, 'pin': 3},  # Release
]

for i, config in enumerate(knobs_config):
    Knob.objects.create(
        preset=preset,
        **config
    )

# 3. Generate firmware (automatically done when downloading)
```

### Frontend Integration Example

```html
<!-- Complete preset configuration page -->
<div class="preset-config">
    <h2>Configure Preset: {{ preset.name }}</h2>
    
    <form method="post">
        {% csrf_token %}
        
        <!-- Preset Settings -->
        <div class="preset-settings">
            <label>Preset Name:</label>
            <input type="text" name="preset_name" value="{{ preset.name }}" required>
            
            <label>MIDI Channel:</label>
            {{ midi_form.midi_channel }}
        </div>
        
        <!-- Knob Configuration -->
        <div class="knob-config">
            <h3>Knob Configuration</h3>
            {{ knob_formset.management_form }}
            
            {% for form in knob_formset %}
                <div class="knob-row">
                    <div class="field">
                        <label>Channel:</label>
                        {{ form.channel }}
                    </div>
                    <div class="field">
                        <label>CC:</label>
                        {{ form.CC }}
                    </div>
                    <div class="field">
                        <label>Min:</label>
                        {{ form.min }}
                    </div>
                    <div class="field">
                        <label>Max:</label>
                        {{ form.max }}
                    </div>
                    <div class="field">
                        <label>Pin:</label>
                        {{ form.pin }}
                    </div>
                    <div class="field">
                        <label>Delete:</label>
                        {{ form.DELETE }}
                    </div>
                </div>
            {% endfor %}
        </div>
        
        <button type="submit">Save Configuration</button>
    </form>
    
    <!-- Download firmware -->
    <a href="/download_firmware/{{ preset.id }}/" class="download-btn">
        Download Firmware
    </a>
</div>
```

### API Integration Example

```javascript
// JavaScript for dynamic knob management
function addKnob() {
    const formset = document.querySelector('.knob-config');
    const totalForms = document.querySelector('#id_form-TOTAL_FORMS');
    const currentCount = parseInt(totalForms.value);
    
    if (currentCount < 16) {
        // Clone last form and update IDs
        const lastForm = document.querySelector('.knob-row:last-child');
        const newForm = lastForm.cloneNode(true);
        
        // Update form IDs and names
        newForm.querySelectorAll('input, select').forEach(input => {
            const name = input.name.replace(/-\d+-/, `-${currentCount}-`);
            const id = input.id.replace(/-\d+-/, `-${currentCount}-`);
            input.name = name;
            input.id = id;
            input.value = '';
        });
        
        formset.appendChild(newForm);
        totalForms.value = currentCount + 1;
    }
}

// Auto-save functionality
function autoSave() {
    const formData = new FormData(document.querySelector('form'));
    fetch('/preset/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    }).then(response => {
        if (response.ok) {
            showMessage('Configuration saved!');
        }
    });
}
```

---

## Error Handling

### Common Error Responses

1. **Authentication Required (401)**
   - Redirect to `/login/`
   - Message: "Authentication required"

2. **Permission Denied (403)**
   - User doesn't own the preset
   - Message: "You are not allowed to be here!!"

3. **Form Validation Errors**
   - Invalid MIDI channel (not 1-16)
   - Invalid CC number (not 0-127)
   - Duplicate CC or pin numbers
   - Missing required fields

4. **File Not Found (404)**
   - Firmware file doesn't exist
   - Preset doesn't exist

### Error Handling Examples

```python
# View error handling
try:
    preset = Preset.objects.get(id=preset_id, owner=request.user)
except Preset.DoesNotExist:
    messages.error(request, 'Preset not found')
    return redirect('dashboard')

# Form validation
if form.is_valid():
    # Process form
    pass
else:
    # Show errors
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f'{field}: {error}')
```

---

## Security Considerations

### Authentication & Authorization

1. **User Authentication**: All configuration endpoints require login
2. **Object-Level Permissions**: Users can only access their own presets
3. **CSRF Protection**: All forms include CSRF tokens
4. **Input Validation**: All forms validate input ranges and types

### Data Validation

1. **MIDI Channel**: Must be 1-16
2. **CC Numbers**: Must be 0-127 and unique per preset
3. **Pin Numbers**: Must be 0-99 and unique per preset
4. **Value Ranges**: Min/max values must be 0-127

### File Security

1. **Firmware Files**: Generated in controlled directory
2. **Download Protection**: Authentication required for firmware downloads
3. **File Naming**: Controlled naming convention prevents directory traversal

---

## Installation & Setup

### Requirements

```txt
Django>=4.2,<5.0
Gunicorn>=20.1,<21.0
```

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access Application**
   - Visit `http://localhost:8000/`
   - Register a new account or login
   - Start creating presets!

### Production Deployment

The project includes `render.yaml` for deployment on Render.com platform.

---

## Contributing

### Code Structure

- `midi/models.py`: Data models
- `midi/views.py`: Business logic and API endpoints
- `midi/forms.py`: Form definitions and validation
- `midi/urls.py`: URL routing
- `midi/templates/`: HTML templates
- `midi/firmware/`: Firmware templates for each microcontroller

### Development Guidelines

1. Follow Django conventions
2. Add proper validation to forms
3. Include authentication on sensitive endpoints
4. Update documentation for new features
5. Test with multiple microcontroller targets

---

This documentation covers all public APIs, functions, and components of the SweetBoxSYNTHAGE system. For additional support or questions, please refer to the source code or contact the development team.