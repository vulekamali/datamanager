from budgetportal.models import PostIndexPage, PostPage
from django.test import Client, TestCase
from mock import MagicMock, patch


class PostsTestCase(TestCase):
    fixtures = ["posts_pages"]

    def setUp(self):
        self.post_index = PostIndexPage.objects.get(id=1)
        # self.post1 = PostPage.objects.get(id=1)
        # self.post2 = PostPage.objects.get(id=2)

    def test_post_index_page(self):
        """Test if post index page displays posts and intro"""
        print("URL1", self.post_index.url_path)
        response = self.client.get(self.post_index.url_path)
        self.assertContains(response, self.post_index.intro)
        # self.assertContains(response, self.post1.title)
        # self.assertContains(response, self.post2.title)

    # def test_post_page(self):
    #     """Test if post page displays correct info"""
    #     print("URL1",self.post1.url_path)
    #     response = self.client.get(self.post1.get_url())
    #     self.assertContains(response, self.post1.title)
