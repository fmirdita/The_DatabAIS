import datetime
import re
from django.db import models

dt = datetime.datetime
SCAN_FORMAT = '[0-9]{3}:[0-9]{8}'

class PersonType(models.Model):
    STAFF = 'STA'
    STUDENT = 'STU'
    FACULTY = 'FAC'
    INSTRUCTOR = 'INS'
    GUEST = 'GST'
    CONSULTANT = "CNS"
    AFFILIATIONS = (
        (STAFF, 'Staff'),
        (FACULTY, 'Faculty'),
        (INSTRUCTOR, 'Instructor'),
        (STUDENT, 'Student'),
        (GUEST, 'Guest'),
        (CONSULTANT, 'Consultant')
    )
    STR_CHOICES = {key: value for (key, value) in AFFILIATIONS}
    name = models.CharField(max_length=3,choices=AFFILIATIONS, unique=True)

    def __str__(self):
        return self.STR_CHOICES[self.name]

class Person(models.Model):
    class Meta:
        verbose_name_plural = 'People'
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    affiliation_type = models.ManyToManyField(PersonType, blank=True)
    email = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=200, blank=True)
    add_to_mailing_list = models.CharField(max_length=1, blank=True, choices=(('N', 'No'),
                                                                              ('Y', 'Yes'),
                                                                              ('A', 'Added')))
    rfid = models.CharField(max_length=12, blank=True)
    join_date = models.DateTimeField('date joined', default=dt.now)

    def get_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_events(self):
        return Event.objects.filter(checkin__visitor=self)

    def get_checkins(self):
        return SignIn.objects.filter(visitor=self)

    def get_visit_count(self):
        return len(SignIn.objects.filter(visitor=self))

    def get_affiliations(self):
        return [a.name for a in self.affiliation_type.all()]

    get_affiliations.short_description = "Affiliations"

    def is_valid(self):
        #there must be at least an rfid or an email
        # rfid and email not already be in the database
        # email, rfid must be valid
        if self.rfid:
            rfid_matcher = re.compile(SCAN_FORMAT)
            if re.search(rfid_matcher, self.rfid):
                return True
            else:
                return False
        elif self.email:
            return True
        else:
            return False

    def __str__(self):
        return self.get_name()

class EventType(models.Model):
    DIAGLOGUE = 'DIA'
    WORKSHOP = 'WKS'
    MEETUP = 'MUP'
    SYMPOSIUM = 'SYM'
    COLLOQUIUM = 'COL'
    MEETING = 'MET'
    FACULTY_MEETING = 'FME'
    WEBINAR = 'WEB'
    EVENT_TYPES = (
        (DIAGLOGUE, 'Dialogue'),
        (WORKSHOP, 'Workshop'),
        (MEETUP, 'Meetup'),
        (SYMPOSIUM, 'Symposium'),
        (COLLOQUIUM, 'Colloquium'),
        (MEETING, 'Meeting'),
        (FACULTY_MEETING, 'Faculty Meeting'),
        (WEBINAR, 'Webinar')
    )
    STR_CHOICES = {key: value for (key, value) in EVENT_TYPES}
    name = models.CharField(max_length=3,choices=EVENT_TYPES, unique=True)

    def __str__(self):
        return self.STR_CHOICES[self.name]

class EventAudienceType(models.Model):
    STAFF = 'STA'
    FACULTY = 'FAC'
    GRADUATE_STUDENTS = 'GRA'
    AUDIENCE_TYPES = (
        (STAFF, 'Academic Support Staff'),
        (FACULTY, 'Faculty'),
        (GRADUATE_STUDENTS, 'Graduate Students')
    )
    STR_CHOICES = {key: value for (key, value) in AUDIENCE_TYPES}
    name = models.CharField(max_length=20,choices=AUDIENCE_TYPES, unique=True)

    def __str__(self):
        return self.STR_CHOICES[self.name]

class Event(models.Model):

    title = models.CharField(max_length=200)
    jira_key = models.CharField(max_length=10, blank=True, unique=True, null=True)
    start = models.DateTimeField(default=dt.now)
    end = models.DateTimeField(blank=True, null=True)
    host = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.ManyToManyField(EventType, blank=True)
    audience_type = models.ManyToManyField(EventAudienceType, blank=True)
    active = models.BooleanField(default=False)
    pre_calculated_attendance = models.IntegerField(default=0, blank=True)

    def is_valid(self):
        if self.title:
            return True
        else:
            return False

    def attendance_count(self):
        return len(SignIn.objects.filter(event__isnull=False, event=self)) + self.get_pre_calculated_attendance()

    def __str__(self):
        return self.title

    def get_pre_calculated_attendance(self):
        if self.pre_calculated_attendance:
            return self.pre_calculated_attendance
        else:
            return 0

class Service(models.Model):
    ETS = 'ETS'
    TLS = 'TLS'
    RIT = 'RIT'
    DH = 'DH'
    CTL = 'CTL'
    LIB = 'LIB'
    PARTNERS = (
        (ETS, 'ETS'),
        (TLS, 'TLS'),
        (RIT, 'Research IT'),
        (DH, 'Digital Humanities'),
        (CTL, 'Center for Teaching and Learning'),
        (LIB, 'Library')
    )
    name = models.CharField(max_length=50)
    # host = models.CharField(max_length=3,
    #                         choices=PARTNERS,
    #                         default=TLS,
    #                         blank=True)
    description = models.TextField(null=True)
    short_name = models.CharField(max_length=20, blank=True, null=True)
    active = models.NullBooleanField(default=True, null=True)
    list_priority = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class SignIn(models.Model):
    class Meta:
        verbose_name = "Sign-in"
    timestamp = models.DateTimeField(default=dt.now)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.CharField(max_length=200, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True)

    def get_reason(self):
        if self.event:
            return str(self.event)
        else:
            return self.service

    def is_valid(self):
        if self.timestamp:
            return True
        else:
            return False

    def __str__(self):
        return "%s - %s here for %s" % (self.pretty_date(), self.person, self.service)

    def pretty_date(self):
        return self.timestamp.strftime('%a. %m/%d %I:%M%p')
