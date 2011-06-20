from django.contrib import admin
from courses.models import Institution, College, Session, SessionInfo, Classification, Level, Course, Section, Meeting

class SectionInline(admin.StackedInline):
    model = Section
class MeetingInline(admin.StackedInline):
    model = Meeting
class SessionInfoInline(admin.TabularInline):
    model = SessionInfo
    extra = 1

class InstitutionAdmin(admin.ModelAdmin):
  pass
class CollegeAdmin(admin.ModelAdmin):
  pass
class MeetingAdmin(admin.ModelAdmin):
  list_display = ['section', 'day', 'start', 'end', 'location', 'room']
class LevelAdmin(admin.ModelAdmin):
  list_display = ['name', 'institution', 'network']
class SessionAdmin(admin.ModelAdmin):
  list_display = ['name', 'slug', 'network']
  prepopulated_fields = {'slug': ('name',)}
  inlines = [SessionInfoInline]
class ClassificationAdmin(admin.ModelAdmin):
  list_display = ['code', 'name', 'network', 'institution', 'college']
  list_filter = ['institution']
class CourseAdmin(admin.ModelAdmin):
  list_display = ['name', 'number', 'classification', 'college', 'level', 'description', 'grading', 'session']
  inlines = [SectionInline]
  list_filter = ['session']
  search_fields = ['name', 'number', 'description', 'profs']
class SectionAdmin(admin.ModelAdmin):
  list_display = ['number', 'reference_code', 'status', 'name', 'course', 'prof', 'units', 'component', 'notes', 'seats_capacity', 'seats_taken', 'seats_available', 'waitlist_capacity', 'waitlist_taken', 'waitlist_available']
  inlines = [MeetingInline]

admin.site.register(Institution, InstitutionAdmin)
admin.site.register(College, CollegeAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Meeting, MeetingAdmin)
