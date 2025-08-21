from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Пользователь")
    display_name = models.CharField("Отображаемое имя", max_length=150, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    homepage = models.URLField("Личный сайт", blank=True)
    bio = models.TextField("О себе", blank=True)
    created_at = models.DateTimeField("Создан", default=timezone.now)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.display_name or f"Профиль {self.user.username}"
