from django.contrib import admin
from django.db.models import get_model
from django.db import models

from courses.models import Institution, College, Session, Course, Section, Classification

class InstitutionAdmin(admin.ModelAdmin):
    pass
    
class CollegeAdmin(admin.ModelAdmin):
    pass

class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    
class SessionAdmin(admin.ModelAdmin):
    pass
    
class SectionAdmin(admin.ModelAdmin):
    list_display = ['course', 'status', 'component', 'number', 'prof', 'units', 'notes',
        'name', 'location', 'room', 'seats_capacity', 'seats_taken', 'seats_available',
        'waitlist_capacity', 'waitlist_taken', 'waitlist_available']
    search_fields = ['name',]
    #list_filter = ['institution',]

class SessionInline(admin.StackedInline):
    model = Section

class CourseAdmin(admin.ModelAdmin):
    inlines = [SessionInline]
    list_filter = ['institution',]
    list_display = ['course_name', 'classification', 'number', 'college', 'level', 'grading', 'description', 'session']

admin.site.register(College, CollegeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course, CourseAdmin)
