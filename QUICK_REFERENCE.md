# SweetBoxSYNTHAGE Quick Reference Guide

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## 📋 URL Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Home page |
| `/dashboard/` | GET | Yes | User presets dashboard |
| `/preset/` | GET/POST | Yes | Configure preset |
| `/create_preset/` | POST | Yes | Create new preset |
| `/delete_preset/<id>/` | GET/POST | Yes | Delete preset |
| `/download_firmware/<id>/` | GET | Yes | Download firmware |
| `/login/` | GET/POST | No | User login |
| `/logout/` | GET | No | User logout |
| `/sign-up/` | GET/POST | No | User registration |

## 💾 Models

### Preset
```python
class Preset(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    keys_channel = models.PositiveSmallIntegerField(default=1)
    number_of_knobs = models.PositiveSmallIntegerField(default=4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
```

### Knob
```python
class Knob(models.Model):
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE)
    channel = models.PositiveSmallIntegerField(default=1)  # 1-16
    CC = models.PositiveSmallIntegerField(default=24)      # 0-127
    min = models.IntegerField(default=0)                   # 0-127
    max = models.IntegerField(default=127)                 # 0-127
    pin = models.IntegerField(default=0)                   # 0-99
```

## 📝 Forms

### Create Preset
```python
# POST /create_preset/
{
    'name': 'My Preset',
    'keys_channel': 1,        # 1-16
    'number_of_knobs': 4      # 1-16
}
```

### Configure Knobs
```python
# POST /preset/
{
    'preset_name': 'Updated Name',
    'midi_channel': 1,        # 1-16
    'form-TOTAL_FORMS': 2,
    'form-0-channel': 1,      # 1-16
    'form-0-CC': 74,          # 0-127
    'form-0-min': 0,          # 0-127
    'form-0-max': 127,        # 0-127
    'form-0-pin': 0,          # 0-99
    # ... more knobs
}
```

## 🛠️ Common Operations

### Create Preset Programmatically
```python
from midi.models import Preset, Knob

# Create preset
preset = Preset.objects.create(
    owner=user,
    name="Bass Controller",
    keys_channel=1,
    number_of_knobs=4
)

# Add knobs
knob_configs = [
    {'channel': 1, 'CC': 74, 'min': 0, 'max': 127, 'pin': 0},  # Filter
    {'channel': 1, 'CC': 71, 'min': 0, 'max': 127, 'pin': 1},  # Resonance
    {'channel': 1, 'CC': 73, 'min': 0, 'max': 127, 'pin': 2},  # Attack
    {'channel': 1, 'CC': 72, 'min': 0, 'max': 127, 'pin': 3},  # Release
]

for config in knob_configs:
    Knob.objects.create(preset=preset, **config)
```

### Query Presets
```python
# Get user presets
presets = Preset.objects.filter(owner=user).order_by('-updated')

# Get preset with knobs
preset = Preset.objects.prefetch_related('knob_set').get(id=preset_id)
knobs = preset.knob_set.all()

# Get knobs for preset
knobs = Knob.objects.filter(preset=preset)
```

## 🔧 Form Validation

### Field Ranges
- **MIDI Channel**: 1-16
- **CC Number**: 0-127
- **Min/Max Values**: 0-127
- **Pin Number**: 0-99

### Validation Rules
- All knob fields required
- Unique CC numbers per preset
- Unique pin numbers per preset
- At least one knob per preset

## 📱 Frontend Integration

### Basic Form
```html
<form method="post">
    {% csrf_token %}
    
    <!-- Preset Settings -->
    <input type="text" name="preset_name" value="{{ preset.name }}" required>
    {{ midi_form.midi_channel }}
    
    <!-- Knobs -->
    {{ knob_formset.management_form }}
    {% for form in knob_formset %}
        {{ form.channel }}
        {{ form.CC }}
        {{ form.min }}
        {{ form.max }}
        {{ form.pin }}
        {{ form.DELETE }}
    {% endfor %}
    
    <button type="submit">Save</button>
</form>
```

### JavaScript Integration
```javascript
// Add new knob form
function addKnob() {
    const totalForms = document.querySelector('#id_form-TOTAL_FORMS');
    const currentCount = parseInt(totalForms.value);
    
    if (currentCount < 16) {
        // Clone and update form
        const newForm = document.querySelector('.knob-row:last-child').cloneNode(true);
        // Update IDs and names...
        totalForms.value = currentCount + 1;
    }
}

// CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

## 🔌 Firmware Generation

### Supported Microcontrollers
- **ATMEGA32U4** (Arduino Leonardo/Micro)
- **ESP32_USB** (ESP32 with USB)
- **RP2040** (Raspberry Pi Pico)

### Generated Firmware Structure
```cpp
// SweetBox SYNTHAGE Firmware
// Preset: {preset_name}
const int NUM_KNOBS = {num_knobs};
int knobChannels[NUM_KNOBS] = { {channels} };
int knobCCs[NUM_KNOBS] = { {ccs} };
int knobMins[NUM_KNOBS] = { {mins} };
int knobMaxs[NUM_KNOBS] = { {maxs} };
```

### Download Firmware
```python
# Generate firmware file
firmware_path = f'generated_firmware/firmware_preset_{preset_id}.ino'

# Download URL
download_url = f'/download_firmware/{preset_id}/'
```

## 🚨 Error Handling

### Common Errors
```python
# Preset not found
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
    # Show errors
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f'{field}: {error}')
```

### Form Validation Errors
- Invalid MIDI channel (not 1-16)
- Invalid CC number (not 0-127)
- Duplicate CC or pin numbers
- Missing required fields

## 🔒 Security Features

### Authentication
- User login required for all configuration
- Session-based authentication
- CSRF protection on all forms

### Authorization
- Users can only access their own presets
- Object-level permissions enforced
- Secure file downloads

### Data Validation
- Input range validation
- Unique constraint validation
- Required field validation

## 📊 Performance Tips

### Database Optimization
```python
# Prefetch related objects
presets = Preset.objects.filter(owner=user).prefetch_related('knob_set')

# Use select_related for foreign keys
knobs = Knob.objects.select_related('preset').filter(preset__owner=user)

# Order by for consistent results
presets = Preset.objects.filter(owner=user).order_by('-updated')
```

### File Operations
```python
# Safe file operations
os.makedirs(firmware_dir, exist_ok=True)
with open(firmware_path, 'w') as f:
    f.write(firmware_content)
```

## 🐛 Debugging

### Debug Settings
```python
# In settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Common Issues
1. **Database not migrated**: Run `python manage.py migrate`
2. **No default preset**: Automatically created on first login
3. **Firmware not generating**: Check file permissions in `generated_firmware/`
4. **Form validation errors**: Check field ranges and uniqueness

## 🚀 Development Workflow

1. **Setup**: Install dependencies, migrate database
2. **Create User**: Register or create superuser
3. **Create Preset**: Use dashboard or API
4. **Configure Knobs**: Use portal interface
5. **Generate Firmware**: Download from portal
6. **Test**: Upload to microcontroller and test

## 📚 References

- **Django Documentation**: https://docs.djangoproject.com/
- **MIDI Specification**: https://www.midi.org/specifications
- **Arduino Reference**: https://www.arduino.cc/reference/

---

This quick reference covers the essential information needed to work with the SweetBoxSYNTHAGE system. For detailed documentation, see `API_DOCUMENTATION.md` and `FUNCTION_REFERENCE.md`.