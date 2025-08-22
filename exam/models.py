from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AZexam(models.Model):
    title = models.CharField("Название экзамена", max_length=255)
    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)
    exam_date = models.DateTimeField("Дата проведения экзамена")
    image = models.ImageField("Изображение с заданием", upload_to="exam_images/", blank=True, null=True)
    participants = models.ManyToManyField(
        User, verbose_name="Участники (пользователи)", related_name="xxexam_participants"
    )
    is_public = models.BooleanField("Опубликовано", default=True)

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.title} ({self.exam_date.strftime('%Y-%m-%d %H:%M')})"

    def is_future(self) -> bool:
        return self.exam_date >= timezone.now()
