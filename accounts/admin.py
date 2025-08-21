from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_name", "homepage", "created_at")
    list_display_links = ("id", "user")
    search_fields = ("user__username", "user__email", "display_name")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    raw_id_fields = ("user",)
