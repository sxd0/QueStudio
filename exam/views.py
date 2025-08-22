from django.conf import settings
from django.shortcuts import render
from .models import AZexam

def azexam_page(request):
    items = (AZexam.objects
             .filter(is_public=True)
             .prefetch_related("participants")
             .order_by("-created_at"))
    ctx = {
        "items": items,
        "full_name": getattr(settings, "EXAM_FULL_NAME", "ФИО"),
        "group": getattr(settings, "EXAM_GROUP", "Группа"),
    }
    return render(request, "exam/list.html", ctx)
