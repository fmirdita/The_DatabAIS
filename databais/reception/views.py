from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.utils import timezone

from .forms import *

logger = logging.getLogger(__name__)

class WelcomeView(TemplateView):

    template_name = 'reception/welcome.html'
    greeting = "Welcome to the AIS!"
    sign_in_blurb = "To sign in, please place your Cal ID on the scanner below."
    form = LookUpForm()

    def post(self, request, *args, **kwargs):
        context = self.post_context_data(request)
        if 'person_id' in context:
            # if it's a consultant, just check them in
            person = Person.objects.get(id=context['person_id'])
            if PersonType.CONSULTANT in person.get_affiliations() and not request.POST.get('event_id'):
                SignIn(person=person,
                       service=Service.objects.get(name='Staff'),
                       timestamp=timezone.now()).save()
                return render(request, 'reception/thanks.html')

        return render(request, 'reception/sign_in.html', context )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['greeting'] = self.greeting
        context['form'] = self.form
        context['sign_in_blurb'] = self.sign_in_blurb
        return context

    def post_context_data(self, request):
        look_up_form = LookUpForm(request.POST)
        if look_up_form.is_valid():
            person = look_up_form.look_up()
            if person and person.email:
                # if we have their email, they do not need to register
                context = {'person_id': person.id}
            else:
                # we don't recognize the rfid scan or email
                registration_form = RegistrationForm({'email': look_up_form.cleaned_data['email'],
                                                      'rfid': look_up_form.cleaned_data['rfid'],
                                                      'add_to_mailing_list': True})
                context = {'registration_form': registration_form}
            context['service_form'] = ServiceForm()
        return context


class EventWelcomeView(WelcomeView):

    def post(self, request, *args, **kwargs):
        context = super().post_context_data(request)
        context['event_id'] = request.POST.get('event_id')
        if 'person_id' in context:
            new_sign_in = SignIn(person=Person.objects.get(id=context['person_id']),
                                 event=Event.objects.get(id=context['event_id']),
                                 timestamp=timezone.now())
            new_sign_in.save()
            return render(request, 'reception/thanks.html', {'event': context['event_id']})
        else:
            return render(request, 'reception/sign_in.html', context )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['greeting'] = "Current Event:"
            context['event'] = Event.objects.get(active=True)
        except Event.DoesNotExist:
            context['greeting'] = "No Current Event"
            context['sign_in_blurb'] = "Activate an event to begin sign-ins."
        return context


def sign_in(request):
    if request.method == "POST":
        person_id = request.POST.get('person_id')
        if person_id:
            person = Person.objects.get(id=person_id)
        else:
            registration_form = RegistrationForm(request.POST)
            if registration_form.is_valid():
                clean_info = registration_form.cleaned_data
                rfid = clean_info['rfid']
                email = clean_info['email']

                # try to update  an existing model
                try:
                    person_rfid = Person.objects.get(rfid=rfid)
                except (Person.DoesNotExist, Person.MultipleObjectsReturned):
                    person_rfid = None

                try:
                    person_email = Person.objects.get(email=email)
                except Person.DoesNotExist:
                    person_email = None

                if person_rfid and person_email:
                    if person_rfid != person_email:
                        # two different people already exist
                        # shouldn't happen
                        pass
                    else:
                        # person already exists and has matching info
                        # shouldn't have filled out info in the first place
                        pass
                elif person_rfid:
                    # person saved with rfid but not email, update
                    person = person_rfid
                    person.first_name = clean_info['first_name']
                    person.last_name = clean_info['last_name']
                    person.email = clean_info['email']
                    person.add_to_mailing_list = clean_info['add_to_mailing_list']
                    person.department = clean_info['department']
                elif person_email:
                    # person saved with email but not rfid
                    if rfid:
                        # we had an rfid with no info, update
                        person = person_email
                        person.first_name = clean_info['first_name']
                        person.last_name = clean_info['last_name']
                        person.email = clean_info['email']
                        person.add_to_mailing_list = clean_info['add_to_mailing_list']
                        person.department = clean_info['department']
                        person.rfid = rfid
                else:
                    # Person does not exist with this email or rfid, make new one.
                    person = Person(first_name=clean_info['first_name'],
                                    last_name=clean_info['last_name'],
                                    email=email,
                                    department=clean_info['department'],
                                    add_to_mailing_list=clean_info['add_to_mailing_list'],
                                    rfid=rfid)

                person.save()

        event_id = request.POST.get('event_id')
        if event_id:
            event_active = True
            event = Event.objects.get(id=event_id)
        else:
            event_active = False

        new_sign_in = SignIn(person = person,
                             timestamp=timezone.now())
        if event_active:
            new_sign_in.event = event
        else:
            if person.affiliation_type == PersonType.CONSULTANT:
                service = Service.objects.get(name="Staff")
            else:
                service = Service.objects.get(id=request.POST.get('service'))
            new_sign_in.service = service

        new_sign_in.save()

        return render(request, 'reception/thanks.html', {'event': event_active})

