from django.test import TestCase
from django.urls import reverse


class CatalogTests(TestCase):
    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_contacts_page_status_code(self):
        response = self.client.get(reverse("contacts"))
        self.assertEqual(response.status_code, 200)
