from django.contrib import admin

from api.models import FriendRequest
from users.models import User


class Admin(admin.ModelAdmin):
    pass


admin.site.register(User, Admin)
admin.site.register(FriendRequest, Admin)
