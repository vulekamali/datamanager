from wagtail.core import blocks


class SectionBlock(blocks.StructBlock):
    presentation_class = blocks.ChoiceBlock(
        choices=[
            ("is-default", "Default"),
            ("is-invisible", "No background/border"),
            ("is-bevel", "Bevel"),
        ]
    )
    heading = blocks.CharBlock()
    content = blocks.RichTextBlock()

    class Meta:
        template = "budgetportal/blocks/section.html"


class DescriptionEmbedBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    description = blocks.RichTextBlock()
    embed_code = blocks.RawHTMLBlock()

    class Meta:
        template = "budgetportal/blocks/description_embed.html"
