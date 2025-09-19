from django.contrib import admin
from .models import Category, Tag, Topic, TopicTag, Post, Comment, Attachment, TopicVote, PostVote
from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.db.models import Count

@admin.action(description="Экспортировать выбранные темы в PDF")
def export_topics_to_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="topics.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50
    for t in queryset.select_related("category", "author"):
        lines = [
            f"Тема: {t.title}",
            f"Категория: {t.category.name}",
            f"Автор: {t.author.username}",
            f"Рейтинг: {t.rating}",
            f"Постов: {t.posts.count()}",
            "-" * 60,
        ]
        for line in lines:
            p.drawString(40, y, line)
            y -= 16
            if y < 60:
                p.showPage()
                y = height - 50
    p.showPage()
    p.save()
    return response

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class TopicTagInline(admin.TabularInline):
    model = TopicTag
    extra = 1
    raw_id_fields = ("tag",)

# @admin.action(description="Экспортировать выбранные темы в PDF")
# def export_topics_to_pdf(modeladmin, request, queryset):
#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = 'attachment; filename="topics.pdf"'
#     p = canvas.Canvas(response, pagesize=A4)
#     width, height = A4
#     y = height - 50
#     p.setFont("Helvetica", 12)
#     for topic in queryset.select_related("category", "author"):
#         line = f"[{topic.id}] {topic.title} — {topic.category.name} — автор: {topic.author.username}"
#         p.drawString(40, y, line[:110])
#         y -= 20
#         if y < 60:
#             p.showPage(); y = height - 50
#     p.showPage()
#     p.save()
#     return response

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "author", "status", "rating", "created_at", "posts_total")
    list_display_links = ("id", "title")
    list_filter = ("status", "category", "created_at", "updated_at", "is_active")
    date_hierarchy = "created_at"
    search_fields = ("title", "author__username", "author__email", "category__name")
    readonly_fields = ("rating", "created_at", "updated_at")
    raw_id_fields = ("author", "category")
    inlines = (PostInline, TopicTagInline)
    prepopulated_fields = {"slug": ("title",)}
    actions = [export_topics_to_pdf]

    list_select_related = ("category", "author")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category", "author").annotate(posts_total=Count("posts"))

    @admin.display(description="Сообщений", ordering="posts_total")
    def posts_total(self, obj):
        return obj.posts_total


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "author", "rating", "is_accepted", "created_at")
    list_display_links = ("id", "topic")
    list_filter = ("is_accepted", "created_at")
    date_hierarchy = "created_at"
    search_fields = ("author__username", "author__email", "topic__title", "body")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("author", "topic")
    inlines = (AttachmentInline,)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "topic", "post", "created_at")
    list_display_links = ("id", "author")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    search_fields = ("author__username", "author__email", "body", "topic__title", "post__body")
    raw_id_fields = ("author", "topic", "post")
    readonly_fields = ("created_at",)


admin.site.register(Attachment)
admin.site.register(TopicTag)
admin.site.register(TopicVote)
admin.site.register(PostVote)
