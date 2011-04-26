from django.contrib import admin
from django.db.models import get_model
from django.db import models

from courses.models import College, Session, Course, Section, Classification

class CollegeAdmin(admin.ModelAdmin):
    pass

class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    
class SessionAdmin(admin.ModelAdmin):
    pass
    
class SectionAdmin(admin.ModelAdmin):
    list_display = ['course', 'section', 'number', 'is_open']
    search_fields = ['class_name',]

class SessionInline(admin.StackedInline):
    model = Section

class CourseAdmin(admin.ModelAdmin):
    inlines = [SessionInline]
    list_filter = ['classification',]
    list_display = ['college', 'course_name', 'classification', 'number']

admin.site.register(College, CollegeAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Course, CourseAdmin)
