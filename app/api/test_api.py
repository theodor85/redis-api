import pytest
from django.urls import reverse


@pytest.fixture
def api_client():
   from rest_framework.test import APIClient
   return APIClient()


def test_get_all(api_client):
   url = reverse('api:all_items')
   response = api_client.get(url)
   assert response.status_code == 200
