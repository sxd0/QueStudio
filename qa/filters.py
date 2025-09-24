import django_filters as df
from django.db.models import Q
from .models import Topic

class TopicFilter(df.FilterSet):
    category = df.CharFilter(field_name="category__slug", lookup_expr="iexact")
    author = df.CharFilter(field_name="author__username", lookup_expr="iexact")
    tag = df.CharFilter(field_name="tags__slug", lookup_expr="iexact")
    created_from = df.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_to = df.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")
    rating_gte = df.NumberFilter(field_name="rating", lookup_expr="gte")
    rating_lte = df.NumberFilter(field_name="rating", lookup_expr="lte")
    q = df.CharFilter(method="filter_q")
    q_cs = df.CharFilter(method="filter_q_cs")

    class Meta:
        model = Topic
        fields = ["category", "author", "tag", "rating_gte", "rating_lte"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(body__icontains=value))

    def filter_q_cs(self, queryset, name, value):
        return queryset.filter(Q(title__contains=value) | Q(body__contains=value))
