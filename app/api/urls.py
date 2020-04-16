from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import all_items, visited_links

app_name = 'api'
urlpatterns = {
    path('visited_links/', visited_links, name="visited_links"),
    # path('/visited_domains', manage_item, name="visited_domains"),
    path('all/', all_items, name="all_items"),
}
urlpatterns = format_suffix_patterns(urlpatterns)