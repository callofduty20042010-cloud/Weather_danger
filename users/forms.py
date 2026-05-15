from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from weather_danger.bulma_mixin import BulmaMixin
from django.contrib.auth import get_user_model

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm(BulmaMixin, UserCreationForm):
  username = forms.CharField(label='Create username')
  email = forms.EmailField(label='Write email')
  password1 = forms.CharField(widget=forms.PasswordInput(), label='Create password')
  password2 = forms.CharField(widget=forms.PasswordInput(), label='Repeat password')

  class Meta:
      model = User
      fields = ('username', 'email', 'password1', 'password2')


class SignInForm(BulmaMixin, AuthenticationForm):
  username = forms.CharField(label='Write username')
  password = forms.CharField(widget=forms.PasswordInput(), label='Write password')

  class Meta:
      model = User
      fields = ('username', 'password')

  
class EditProfileForm(BulmaMixin, forms.ModelForm):
   first_name = forms.CharField(label='Write first name')
   last_name = forms.CharField(label='Write last name')
   username = forms.CharField(label='Write username')
   email = forms.EmailField(label='Write email')

   class Meta:
      model = User
      fields = ('first_name', 'last_name', 'username', 'email')

class ResetPasswordForm(BulmaMixin, forms.Form):
   old_password = forms.CharField(widget=forms.PasswordInput(), label='Write old password')
   new_password = forms.CharField(widget=forms.PasswordInput(), label='Write new password')
   new_password2 = forms.CharField(widget=forms.PasswordInput(), label='Repeat new password')

   class Meta:
      model = User
      fields = ('old_password', 'new_password', 'new_password2')
   