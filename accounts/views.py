from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, IntegerField, F, Value


from .models import Profile
from .serializers import RegisterSerializer, ProfileSerializer

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TopUsersAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = (User.objects
                 .annotate(topic_rating=Coalesce(Sum("topics__rating"), 0))
                 .annotate(post_rating=Coalesce(Sum("posts__rating"), 0))
                 .annotate(total_rating=F("topic_rating") + F("post_rating"))
                 .annotate(posts_count=Coalesce(Count("posts"), 0))
                 .annotate(topics_count=Coalesce(Count("topics"), 0))
                 .order_by("-total_rating", "-posts_count")[:10]
                 )
        data = [
            {
                "username": u.username,
                "display_name": getattr(getattr(u, "profile", None), "display_name", "") or u.username,
                "total_rating": u.total_rating,
                "posts": u.posts_count,
                "topics": u.topics_count,
            } for u in users
        ]
        return Response(data)