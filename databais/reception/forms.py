from django import forms
from .models import *
import re
import logging

logger = logging.getLogger(__name__)

class LookUpForm(forms.Form):
    rfid = forms.CharField(max_length=12, required=False)
    email = forms.EmailField(initial='email address', required=False,\
                             widget=forms.EmailInput(attrs={'onFocus': 'this.select()'}))

    def clean_rfid(self):
        return self.cleaned_data['rfid']

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def look_up(self):
        # returns a person if they already exist in the database
        # else returns None
        if self.cleaned_data['rfid']:
            try:
                person = Person.objects.get(rfid=self.cleaned_data['rfid'])
            except Person.DoesNotExist:
                return None
        else:
            try:
                person = Person.objects.get(email=self.cleaned_data['email'])
            except Person.DoesNotExist:
                return None
        return person

class RegistrationForm(forms.ModelForm):

    add_to_mailing_list = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'email', 'department', 'affiliation_type', 'add_to_mailing_list', 'rfid')
        labels = {
            'add_to_mailing_list': ("Keep up updated on upcoming events!"),
            'first_name': ('First Name:'),
            'last_name': ('Last Name:'),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_first_name(self):
        return self.cleaned_data['first_name'].capitalize()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].capitalize()

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean_add_to_mailing_list(self):
        if self.cleaned_data['add_to_mailing_list']:
            return 'Y'
        else:
            return 'N'

class ServiceForm(forms.Form):

    service = forms.ModelChoiceField(queryset=Service.objects.filter(active=True).order_by('list_priority'),
                                     empty_label= None,
                                     label= "What brings you in today?",
                                     widget=forms.RadioSelect(),
                                     required=True)

