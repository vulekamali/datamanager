from django.core.files.images import ImageFile
from django.test import Client, TestCase
from budgetportal.models import GuideIndexPage, GuidePage, CategoryGuide


class GuideIndexPageTestCase(TestCase):
    fixtures = ["test-guides-pages"]

    def setUp(self):
        self.guide_index_page = GuideIndexPage.objects.get(id=4)
        self.guide_page = GuidePage.objects.get(id=5)
        self.category_guides = CategoryGuide.objects.all()

    def test_guide_index_page(self):
        """Simple test of template response for guide index page"""
        response = Client().get(self.guide_index_page.url_path)
        self.assertContains(response, self.guide_index_page.title)
        self.assertContains(response, self.guide_index_page.intro)

        self.assertGreaterEqual(self.category_guides.count(), 1)

        for category_guide in self.category_guides:
            self.assertContains(response, category_guide.external_url_title)
            self.assertContains(response, category_guide.external_url_description)


class GuidePagesTestCase(TestCase):
    fixtures = ["test-guides-pages"]

    def setUp(self):
        self.guide_page = GuidePage.objects.get(id=5)

    def test_guide_page(self):
        """Simple test of template response for guide page"""
        with open("budgetportal/tests/test_data/photo.jpg", "rb") as file:
            self.guide_page.image.file = ImageFile(file, "photo.jpg")
            self.guide_page.image.save()

        response = Client().get(self.guide_page.url_path)
        self.assertContains(response, self.guide_page.title)
        self.assertIsNotNone(self.guide_page.image)
        ## Verify the integration of our configuration, django-storages and wagtail
        ## - that is - the generated image URL templated in matches the configuration of the site
        self.assertContains(
            response,
            "http://minio:9000/budgetportal-storage/images/photo.max-320x200.jpg",
        )

        for body_part in self.guide_page.body:
            self.assertContains(response, body_part)
