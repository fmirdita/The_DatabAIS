from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from .models import *
from .forms import *
from .resources import *
from django.urls import reverse
from django.utils.html import format_html

admin.site.site_header = 'TheDatabais'
admin.site.site_title = 'TheDatabais'
admin.site.index_title = 'AIS Administration'


class databaisInline(admin.TabularInline):
    extra = 0
    classes = ('collapse',)

class PersonInline(databaisInline):
    model = Person


class SignInInline(databaisInline):
    model = SignIn
    fields = ['timestamp', 'person', 'service', 'comments']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(service__isnull=False)


class SignInEventInline(databaisInline):
    model = SignIn
    verbose_name = "Event Sign-in"
    verbose_name_plural = "Event Sign-ins"
    fields = ('timestamp','person', 'event', 'comments')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(event__isnull=False)

@admin.register(PersonType)
class PersonTypeAdmin(ImportExportActionModelAdmin):
    resource_class = PersonTypeResource

@admin.register(Person)
class PersonAdmin(ImportExportActionModelAdmin):
    inlines = (SignInInline, SignInEventInline,)
    resource_class = PersonResource
    date_hierarchy = 'join_date'
    search_fields =  ['first_name', 'last_name', 'email', 'department']
    list_display = ( 'date_joined', 'name', 'get_affiliations', 'add_to_mailing_list')
    # list_editable = ( '',)
    list_filter = ('join_date',)
    list_display_links = ('name',)
    ordering = ('-join_date', 'last_name')

    def name(self, obj):
        return obj.__str__()

    def date_joined(self, obj):
        return obj.join_date.date()


@admin.register(EventType)
class EventTypeAdmin(ImportExportActionModelAdmin):
    resource_class = EventTypeResource

@admin.register(EventAudienceType)
class EventAudienceTypeAdmin(ImportExportActionModelAdmin):
    resource_class = EventAudienceTypeResource

@admin.register(Event)
class EventAdmin(ImportExportActionModelAdmin):
    inlines = (SignInEventInline,)
    resource_class = EventResource
    date_hierarchy = 'start'
    search_fields = ['title', 'jira_key', 'host', 'event_type', 'audience_type', ]
    list_display = ('date_of_event', 'title', 'jira_key', 'active', 'attendance_count')
    list_editable = ('active',)
    fields = ('title', ('start', 'end'), 'attendance_count', 'description', ('event_type', 'audience_type'), 'pre_calculated_attendance', 'jira_key', 'active')
    ordering = ('-start',)
    # form = EventForm
    # fieldsets = (
    #     (None, {
    #         'fields': ('title', 'date', 'attendance_count', 'description', ('event_type', 'audience_type'), 'pre_calculated_attendance', 'jira_key', 'active')
    #     }),
    #     ('Additional Fields', {
    #         'classes': ('collapse',),
    #         'fields': ('description', ('event_type', 'audience_type'), 'pre_calculated_attendance', 'jira_key', 'active'),
    #     }),
    # )
    readonly_fields = ['attendance_count']

    def date_of_event(self, obj):
        return obj.start.date()

    def attendance_count(self, obj):
        return obj.attendance_count()

@admin.register(Service)
class ServiceAdmin(ImportExportActionModelAdmin):
    resource_class = ServiceResource
    list_display = ('name', 'description', 'active', 'list_priority')
    list_editable = ('active', 'list_priority')

@admin.register(SignIn)
class SignInAdmin(ImportExportActionModelAdmin):
    list_per_page = 20
    date_hierarchy = 'timestamp'
    search_fields = ['person__email', 'person__first_name', 'person__last_name', 'service__name']
    list_display = ('timestamp', 'link_to_person','link_to_event', 'service', 'comments', )
    list_select_related = ('service', 'person')
    list_display_links = ('timestamp',)
    list_editable = ('service', 'comments')
    ordering = ('-timestamp',)

    def summary(self, obj):
        return "Sign-in: " + obj.pretty_date()

    def link_to_person(self, obj):
        if obj.person:
            link = reverse("admin:reception_person_change", args=[obj.person.id])
        else:
            link = None
        return format_html('<a href="{}">{}</a>', link, obj.person)

    link_to_person.short_description = 'Person'

    def link_to_event(self, obj):
        if obj.event:
            link = reverse("admin:reception_event_change", args=[obj.event.id])
            return format_html('<a href="{}">{}</a>', link, obj.event)
        else:
            return None





