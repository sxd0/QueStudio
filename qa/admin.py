from django.contrib import admin
from .models import Category, Tag, Topic, TopicTag, Post, Comment, Attachment, TopicVote, PostVote

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

    @admin.display(description="Сообщений")
    def posts_total(self, obj):
        return obj.posts.count()


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
