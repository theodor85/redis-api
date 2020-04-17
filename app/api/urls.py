from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import all_items, visited_links, visited_domains, clear

app_name = 'api'
urlpatterns = {
    path('visited_links/', visited_links, name="visited_links"),
    path('visited_domains/', visited_domains, name="visited_domains"),
    path('all/', all_items, name="all_items"),
    path('clear/', clear, name="clear"),
}
urlpatterns = format_suffix_patterns(urlpatterns)
