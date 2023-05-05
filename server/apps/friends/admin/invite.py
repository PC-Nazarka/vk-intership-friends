from django.contrib import admin

from apps.friends.models import Invite


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target",
        "is_accept",
        "owner",
    )
