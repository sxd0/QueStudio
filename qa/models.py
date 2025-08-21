from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Avg, Max
from django.core.validators import MinLengthValidator

User = get_user_model()


class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=120, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("qa:category_detail", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField("Тег", max_length=50, unique=True)
    slug = models.SlugField("Слаг", max_length=60, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class TopicManager(models.Manager):
    def hot(self):
        """Темы с активностью за последние 7 дней (посты/оценки)."""
        week_ago = timezone.now() - timezone.timedelta(days=7)
        qs = (self.get_queryset()
              .filter(created_at__gte=week_ago)
              .annotate(posts_count=Count("posts", distinct=True))
              .annotate(avg_post_rating=Avg("posts__rating"))
              .annotate(last_activity=Max("posts__created_at"))
              .order_by("-posts_count", "-last_activity", "-rating"))
        return qs


class Topic(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        PUBLISHED = 1, "Опубликована"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="topics", verbose_name="Категория")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="topics", verbose_name="Автор")
    title = models.CharField("Заголовок", max_length=200, validators=[MinLengthValidator(5)])
    slug = models.SlugField("Слаг", max_length=220)
    body = models.TextField("Текст", validators=[MinLengthValidator(10)])
    status = models.IntegerField("Статус", choices=Status.choices, default=Status.PUBLISHED)
    tags = models.ManyToManyField(Tag, through="TopicTag", related_name="topics", verbose_name="Теги", blank=True)

    rating = models.IntegerField("Суммарный рейтинг", default=0)
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Создана", default=timezone.now)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    objects = TopicManager()

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        unique_together = (("category", "slug"),)
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.title} ({self.category})"

    def get_absolute_url(self):
        return reverse("qa:topic_detail", kwargs={"slug": self.slug})


class TopicTag(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topic_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="tag_topics")

    class Meta:
        verbose_name = "Связь Тема-Тег"
        verbose_name_plural = "Связи Тема-Тег"
        unique_together = (("topic", "tag"),)


class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts", verbose_name="Тема")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор")
    body = models.TextField("Текст", validators=[MinLengthValidator(3)])
    rating = models.IntegerField("Рейтинг", default=0)
    is_accepted = models.BooleanField("Помечен как ответ", default=False)
    created_at = models.DateTimeField("Создан", default=timezone.now)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"Post #{self.pk} в {self.topic}"


class Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField("Текст", validators=[MinLengthValidator(2)])
    created_at = models.DateTimeField("Создан", default=timezone.now)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self) -> str:
        target = self.post or self.topic
        return f"Комментарий к {target} от {self.author}"


class Attachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachments", verbose_name="Пост")
    file = models.FileField("Файл", upload_to="attachments/")
    uploaded_at = models.DateTimeField("Загружен", default=timezone.now)

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"
        ordering = ("-uploaded_at",)

    def __str__(self) -> str:
        return f"Файл {self.file.name} к посту {self.post_id}"


class TopicVote(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="topic_votes")
    value = models.SmallIntegerField(choices=((-1, "Минус"), (1, "Плюс")))

    class Meta:
        verbose_name = "Голос за тему"
        verbose_name_plural = "Голоса за темы"
        unique_together = (("topic", "user"),)


class PostVote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_votes")
    value = models.SmallIntegerField(choices=((-1, "Минус"), (1, "Плюс")))

    class Meta:
        verbose_name = "Голос за сообщение"
        verbose_name_plural = "Голоса за сообщения"
        unique_together = (("post", "user"),)
