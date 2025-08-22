from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction
import random
from qa.models import Category, Tag, Topic, TopicTag, Post, Comment, Attachment, TopicVote, PostVote
from accounts.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds database with demo data for QueStudio (categories, tags, topics, posts, comments, votes, attachments)."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=10, help="Users to create (min 2).")
        parser.add_argument("--topics", type=int, default=20)
        parser.add_argument("--posts_per_topic_min", type=int, default=2)
        parser.add_argument("--posts_per_topic_max", type=int, default=4)
        parser.add_argument("--comments_per_post_min", type=int, default=1)
        parser.add_argument("--comments_per_post_max", type=int, default=3)

    @transaction.atomic
    def handle(self, *args, **opts):
        users_n = max(2, opts["users"])
        topics_n = opts["topics"]
        pmin = opts["posts_per_topic_min"]
        pmax = opts["posts_per_topic_max"]
        cmin = opts["comments_per_post_min"]
        cmax = opts["comments_per_post_max"]

        self.stdout.write(self.style.WARNING("Seeding demo data..."))

        users = []
        for i in range(users_n):
            uname = f"demo{i+1}"
            user, created = User.objects.get_or_create(username=uname, defaults={"email": f"{uname}@example.com"})
            if created:
                user.set_password("pass12345")
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user, defaults={
                "display_name": f"Demo {i+1}",
                "bio": "Учебный пользователь",
            })
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"Users: {len(users)} (пароль у всех: pass12345)"))

        cat_data = [
            ("Python", "python"),
            ("Django", "django"),
            ("Databases", "db"),
            ("Frontend", "frontend"),
            ("DevOps", "devops"),
            ("Algorithms", "algo"),
            ("Security", "sec"),
            ("Networking", "net"),
            ("Testing", "test"),
            ("Other", "other"),
        ]
        categories = []
        for name, slug in cat_data:
            c, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )
            if not c.name:
                c.name = name
                c.save(update_fields=["name"])
            categories.append(c)
        self.stdout.write(self.style.SUCCESS(f"Categories: {len(categories)}"))

        tag_data = [
            ("django", "django"), ("drf", "drf"), ("vue", "vue"), ("react", "react"),
            ("docker", "docker"), ("postgres", "postgres"), ("nginx", "nginx"),
            ("celery", "celery"), ("oauth2", "oauth2"), ("pytest", "pytest"),
            ("sql", "sql"), ("orm", "orm"),
        ]
        tags = []
        for name, slug in tag_data:
            t, _ = Tag.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )
            if not t.name:
                t.name = name
                t.save(update_fields=["name"])
            tags.append(t)
        self.stdout.write(self.style.SUCCESS(f"Tags: {len(tags)}"))

        topics = []
        for i in range(topics_n):
            cat = random.choice(categories)
            author = random.choice(users)
            title = f"Тема #{i+1}: {random.choice(['вопрос','помогите','как сделать','разобраться'])} {cat.name}"
            slug = f"topic-{i+1}-{cat.slug}"
            body = f"Учебный текст по теме {cat.name}. Пример содержимого."
            topic, _ = Topic.objects.get_or_create(
                category=cat, slug=slug,
                defaults={"author": author, "title": title, "body": body, "status": Topic.Status.PUBLISHED}
            )
            for t in random.sample(tags, k=random.randint(2, 3)):
                TopicTag.objects.get_or_create(topic=topic, tag=t)
            topics.append(topic)

        self.stdout.write(self.style.SUCCESS(f"Topics: {len(topics)}"))

        posts_created = 0
        comments_created = 0
        attachments_created = 0
        topic_votes_created = 0
        post_votes_created = 0

        for topic in topics:
            for _ in range(random.randint(pmin, pmax)):
                author = random.choice(users)
                p = Post.objects.create(
                    topic=topic, author=author,
                    body=f"Ответ от {author.username} на {topic.title}"
                )
                posts_created += 1

                if random.random() < 0.5:
                    content = ContentFile(b"Demo attachment content", name=f"note-{p.id}.txt")
                    Attachment.objects.create(post=p, file=content)
                    attachments_created += 1

                for _ in range(random.randint(cmin, cmax)):
                    cauthor = random.choice(users)
                    Comment.objects.create(post=p, author=cauthor, body=f"Комментарий от {cauthor.username}")
                    comments_created += 1

                voters = random.sample(users, k=random.randint(2, min(5, len(users))))
                for voter in voters:
                    if voter.id != p.author_id:
                        value = random.choice([-1, 1, 1])
                        PostVote.objects.get_or_create(post=p, user=voter, defaults={"value": value})
                        p.rating += value
                        post_votes_created += 1
                p.save(update_fields=["rating"])

            voters = random.sample(users, k=random.randint(3, min(7, len(users))))
            for voter in voters:
                if voter.id != topic.author_id:
                    value = random.choice([-1, 1, 1])
                    TopicVote.objects.get_or_create(topic=topic, user=voter, defaults={"value": value})
                    topic.rating += value
                    topic_votes_created += 1
            topic.save(update_fields=["rating"])

        self.stdout.write(self.style.SUCCESS(
            f"Posts: {posts_created}, Comments: {comments_created}, "
            f"Attachments: {attachments_created}, TopicVotes: {topic_votes_created}, PostVotes: {post_votes_created}"
        ))
        self.stdout.write(self.style.SUCCESS("Seeding done."))
