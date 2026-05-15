from django import forms

from .models import (
    Comment,
    EventForecast,
    EventTimelineItem,
    Profile,
    SafetySignal,
    SavedLocation,
    WeatherEvent,
)


COMMON_INPUT = {'class': 'input'}
COMMON_TEXTAREA = {'class': 'textarea'}


class EventForm(forms.ModelForm):
    class Meta:
        model = WeatherEvent
        fields = [
            'title', 'description', 'wind_speed', 'humidity', 'temperature', 'region',
            'event_type', 'danger_level', 'status', 'credibility_score', 'radius_km',
            'latitude', 'longitude',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'credibility_score': forms.NumberInput(attrs={'class': 'input', 'min': 0, 'max': 100}),
        }


class ProfileForm(forms.ModelForm):
    delete_avatar = forms.BooleanField(required=False, label='Delete avatar')

    class Meta:
        model = Profile
        fields = [
            'nickname', 'avatar', 'first_name', 'last_name', 'bio', 'phone', 'birth_date',
            'gender', 'country', 'city', 'address', 'latitude', 'longitude',
            'emergency_contact_name', 'emergency_contact_phone', 'blood_type',
            'medical_conditions', 'safety_notes', 'preferred_language', 'timezone',
            'occupation', 'organization',
        ]
        widgets = {
            'nickname': forms.TextInput(attrs={'placeholder': 'Enter your nickname'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Tell us about yourself', 'rows': 3}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter your country'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter your city'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter your full address'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': '41.3111'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': '69.2797'}),
            'emergency_contact_name': forms.TextInput(attrs={'placeholder': 'Enter contact name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'placeholder': 'Enter contact phone'}),
            'medical_conditions': forms.TextInput(attrs={'placeholder': 'Enter allergies or conditions'}),
            'safety_notes': forms.Textarea(attrs={'placeholder': 'Что важно знать спасателям?', 'rows': 3}),
            'occupation': forms.TextInput(attrs={'placeholder': 'Enter your occupation'}),
            'organization': forms.TextInput(attrs={'placeholder': 'Enter organization'}),
            'timezone': forms.TextInput(attrs={'placeholder': 'Asia/Tashkent'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'image', 'location_text', 'latitude', 'longitude']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'textarea',
                'placeholder': 'Напишите, что происходит рядом с вами...',
                'rows': 4,
                'required': True,
            }),
            'location_text': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Например: Ташкент, Чиланзар или 41.3111, 69.2797',
            }),
            'latitude': forms.NumberInput(attrs={'class': 'input', 'step': 'any', 'placeholder': 'Latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'input', 'step': 'any', 'placeholder': 'Longitude'}),
        }
        labels = {
            'text': 'Комментарий',
            'image': 'Фото с места',
            'location_text': 'Моя геолокация',
            'latitude': 'Широта',
            'longitude': 'Долгота',
        }


class SavedLocationForm(forms.ModelForm):
    class Meta:
        model = SavedLocation
        fields = ['name', 'location_type', 'address', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Home / Work / School / Family'}),
            'address': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Адрес или ориентир'}),
            'latitude': forms.NumberInput(attrs={'class': 'input', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'input', 'step': 'any'}),
        }


class SafetySignalForm(forms.ModelForm):
    class Meta:
        model = SafetySignal
        fields = ['signal_type', 'message', 'location_text', 'latitude', 'longitude']
        widgets = {
            'message': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Короткое сообщение'}),
            'location_text': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Где вы сейчас?'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class TimelineItemForm(forms.ModelForm):
    class Meta:
        model = EventTimelineItem
        fields = ['title', 'description', 'happened_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'happened_at': forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'}),
        }


class ForecastForm(forms.ModelForm):
    class Meta:
        model = EventForecast
        fields = ['title', 'details', 'trend', 'expected_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'details': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'expected_at': forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'}),
        }
