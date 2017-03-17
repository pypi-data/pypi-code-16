from django.contrib import admin

from .models import Faculty
from .models import Department
from .models import AcademicGroup


class GlossaryAdmin(admin.ModelAdmin):
    exclude = ("uuid", )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Faculty)
class FacultyAdmin(GlossaryAdmin):
    readonly_fields = ("name", )


@admin.register(Department)
class DepartmentAdmin(GlossaryAdmin):
    readonly_fields = ("name", "faculty")


@admin.register(AcademicGroup)
class AcademicGroupAdmin(GlossaryAdmin):
    readonly_fields = ("name", "faculty", "year")
