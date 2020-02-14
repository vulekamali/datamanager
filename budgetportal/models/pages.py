from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks as wagtail_blocks
from blocks import SectionBlock
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from django.db import models
from wagtail.wagtailcore.fields import RichTextField

from budgetportal import nav_bar
from .gov_structure import FinancialYear


class WagtailHomePage(Page):
    parent_page_types = []

    class Meta:
        app_label = 'budgetportal'


class LearningIndexPage(Page):
    parent_page_types = []


class PostIndexPage(Page):
    parent_page_types = []
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]


class GuideIndexPage(Page):
    max_count = 1
    parent_page_types = ['budgetportal.LearningIndexPage']
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]


class NavContextMixin(object):

    def get_context(self, request):
        context = super(NavContextMixin, self).get_context(request)
        nav = nav_bar.get_items(FinancialYear.get_latest_year().slug)

        context["navbar"] = nav

        for item in nav:
            if item["url"] and request.path.startswith(item["url"]):
                context["selected_tab"] = item["id"]

        return context


class PostPage(NavContextMixin, Page):
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


class GuidePage(NavContextMixin, Page):
    parent_page_types = ['budgetportal.GuideIndexPage']
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
