from main.models import Department
from main.models import TaskType
from main.models import Profile
from main.models import UserManager
from main.models import SmitTask



from django.contrib import admin

admin.site.register(UserManager)
admin.site.register(Department)
admin.site.register(Profile)
admin.site.register(TaskType)
admin.site.register(SmitTask)


