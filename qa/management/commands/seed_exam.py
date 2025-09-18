from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from io import BytesIO
from PIL import Image

from exam.models import AZexam

class Command(BaseCommand):
    help = "Seed exam data (control work). Creates 5 public AZexam records."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--if-empty", action="store_true")

    def handle(self, *args, **options):
        User = get_user_model()

        if options["if_empty"] and AZexam.objects.exists():
            self.stdout.write("AZexam already populated, skipping.")
            return

        if options["reset"]:
            AZexam.objects.all().delete()

        participants = list(User.objects.all()[:3])
        while len(participants) < 3:
            idx = len(participants) + 1
            u = User.objects.create_user(
                username=f"exam_user_{idx}",
                email=f"exam_user_{idx}@example.com",
                password="exam_user_pass",
            )
            participants.append(u)

        def make_image_bytes():
            img = Image.new("RGB", (200, 100), (220, 220, 220))
            bio = BytesIO()
            img.save(bio, format="PNG")
            return bio.getvalue()

        now = timezone.now()
        items = []
        for i in range(1, 6):
            exam_date = now + timezone.timedelta(days=i)
            obj = AZexam.objects.create(
                title=f"Экзамен №{i}",
                exam_date=exam_date,
                is_public=True,
            )
            img_bytes = make_image_bytes()
            obj.image.save(f"exam_{i}.png", ContentFile(img_bytes), save=True)
            obj.participants.set(participants[:2 + (i % 2)])
            items.append(obj)

        self.stdout.write(f"Created {len(items)} AZexam records.")
