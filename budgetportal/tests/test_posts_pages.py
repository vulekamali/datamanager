from django.test import Client, TestCase
from budgetportal.tests.helpers import WagtailPageTestCase
from budgetportal.models import PostIndexPage, PostPage, FinancialYear


class PostIndexPageTestCase(WagtailPageTestCase):
    fixtures = ["test-posts-pages"]

    def setUp(self):
        FinancialYear.objects.create(slug="2019-20", published=True)
        self.post_index_page = PostIndexPage.objects.get(id=6)
        self.post_page = PostPage.objects.get(id=7)

    def test_post_index_page(self):
        """Simple test of template response for post index page"""
        response = Client().get(self.post_index_page.url_path)
        self.assertContains(response, self.post_index_page.title)
        self.assertContains(response, self.post_index_page.intro)
        self.assertContains(response, self.post_page.title)


class PostPagesTestCase(TestCase):
    fixtures = ["test-posts-pages"]

    def setUp(self):
        FinancialYear.objects.create(slug="2019-20", published=True)
        self.post_page = PostPage.objects.get(id=7)

    def test_post_page(self):
        """Simple test of template response for post page"""
        response = Client().get(self.post_page.url_path)
        self.assertContains(response, self.post_page.title)
        for body_part in self.post_page.body:
            self.assertContains(response, body_part)
