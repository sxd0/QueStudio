from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryViewSet, TagViewSet, TopicViewSet, PostViewSet, CommentViewSet

app_name = "qa"

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"topics", TopicViewSet, basename="topic")
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]
