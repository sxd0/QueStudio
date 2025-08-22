from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from .models import AZexam  

@admin.register(AZexam) 
class AZexamAdmin(admin.ModelAdmin): 
    list_display = ("title", "exam_date", "is_public", "created_at", "participants_count", "thumb")
    list_display_links = ("title",)
    search_fields = ("title", "participants__email")  
    list_filter = (
        "is_public",
        ("created_at", DateFieldListFilter), 
        ("exam_date", DateFieldListFilter), 
    )
    filter_horizontal = ("participants",) 
    readonly_fields = ()
    date_hierarchy = "created_at"

    @admin.display(description="Кол-во участников")
    def participants_count(self, obj):
        return obj.participants.count()

    @admin.display(description="Превью")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px"/>', obj.image.url)
        return "—"
