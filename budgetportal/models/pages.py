from blocks import SectionBlock
from budgetportal import nav_bar
from collections import OrderedDict
from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks as wagtail_blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.contrib.routable_page.models import RoutablePage, route


from .gov_structure import FinancialYear


class WagtailHomePage(RoutablePage):
    max_count = 1


class LearningIndexPage(RoutablePage):
    max_count = 1


class PostIndexPage(RoutablePage):
    max_count = 1
    parent_page_types = []
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    @route(r'^posts/')
    def main(self, request):
        from django.shortcuts import render
        return render(request, self.get_template(request), self.get_context(request))


class PostPage(RoutablePage):
    parent_page_types = ['budgetportal.PostIndexPage']
    body = StreamField([
        ('section', SectionBlock()),
        ('html', wagtail_blocks.RawHTMLBlock()),
    ])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]


class GuideIndexPage(RoutablePage):
    max_count = 1
    parent_page_types = ['budgetportal.LearningIndexPage']
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    # def get_context(self, request, *args, **kwargs):
    #     context = super().get_context(request, *args, **kwargs)
    #     guides_ordering = OrderedDict([(p.title, p) for p in self.get_children()])
    #     for external in CategoryGuide.objects.filter(external_url__isnull=False):
    #         guides_ordering[external.external_url_title] = external
    #         context["guides"] = guides_ordering.values()
    #     return context


class GuidePage(RoutablePage):
    parent_page_types = ["budgetportal.GuideIndexPage"]
    body = StreamField(
        [("section", SectionBlock()), ("html", wagtail_blocks.RawHTMLBlock()), ]
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]


# class CategoryGuide(models.Model):
#     """Link GuidePages or external URLs to dataset category slugs"""
#
#     category_slug = models.SlugField(max_length=200, unique=True)
#     guide_page = models.ForeignKey(
#         GuidePage, null=True, blank=True, on_delete=models.CASCADE
#     )
#     external_url = models.URLField(null=True, blank=True)
#     external_url_title = models.CharField(
#         max_length=200,
#         null=True,
#         blank=True,
#         help_text=(
#             "Only shown if External URL is used. This may be truncated so "
#             "use a short description that will also be seen on the external page."
#         )
#     )
#     external_url_description = models.TextField(
#         null=True,
#         blank=True,
#         help_text=(
#             "Only shown if External URL is used. This may be truncated so "
#             "use a short description that will also be seen on the external page."
#         )
#     )
#
#     def __str__(self):
#         return "{} - {}".format(self.category_slug, self.guide_page or self.external_url)
#
#     def clean(self):
#         if self.external_url is None and self.guide_page is None:
#             raise ValidationError("Either Guide Page or External URL must be set.")
#         if self.external_url is not None and self.guide_page is not None:
#             raise ValidationError("Only one of Guide Page or External URL may be set.")
#         if self.external_url is not None and self.external_url_title is None:
#             raise ValidationError("Title is required when using External URL.")
#
#         return super().clean()
#
#
# class NavContextMixin:
#     def get_context(self, request):
#         context = super().get_context(request)
#         nav = nav_bar.get_items(FinancialYear.get_latest_year().slug)
#
#         context["navbar"] = nav
#
#         for item in nav:
#             if item["url"] and request.path.startswith(item["url"]):
#                 context["selected_tab"] = item["id"]
#
#         return context
