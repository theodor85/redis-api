from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import all_items

app_name = 'api'
urlpatterns = {
    # path('/visited_links', manage_items, name="visited_links"),
    # path('/visited_domains', manage_item, name="visited_domains"),
    path('all/', all_items, name="all_items"),
}
urlpatterns = format_suffix_patterns(urlpatterns)