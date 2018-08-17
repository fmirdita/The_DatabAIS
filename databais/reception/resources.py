from import_export import resources, widgets, fields
from .models import *


class PersonTypeResource(resources.ModelResource):
    class Meta:
        model = PersonType


class PersonResource(resources.ModelResource):
    class Meta:
        model = Person


class EventTypeResource(resources.ModelResource):
    class Meta:
        model = EventType


class EventAudienceTypeResource(resources.ModelResource):
    class Meta:
        model = EventAudienceType


class EventResource(resources.ModelResource):
    class Meta:
        model = Event


class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service


class rfidEmailLookup(widgets.Widget):
    def clean(self, value, row=None, *args, **kwargs):
        rfid_matcher = re.compile(SCAN_FORMAT)
        # if it's an integer, look up by id
        if type(value) is int:
            try:
                person = Person.objects.get(id=value)
                return person
            except Person.DoesNotExist:
                person = None
        # if it's an rfid, look up person
        elif re.search(rfid_matcher, value):
            try:
                person = Person.objects.get(rfid=value)
            except Person.DoesNotExist:
                person = Person(rfid=value)
                person.save()
        # otherwise look up by email
        else:
            try:
                person = Person.objects.get(email=value)
            except Person.MultipleObjectsReturned:
                person = None
        # if no person exists, create a new one with the email
        return person

    def render(self, value, obj=None):
        if type(value) is Person:
            return Person.id


class eventLookup(widgets.Widget):
    def clean(self, value, row=None, *args, **kwargs):
        try:
            return Event.objects.get(key=value)
        except Event.DoesNotExist:
            return None


class SignInResource(resources.ModelResource):
    person = fields.Field(column_name='person', attribute='person', widget=rfidEmailLookup())
    event = fields.Field(column_name='event', attribute='event', widget=eventLookup())

    class Meta:
        model = SignIn