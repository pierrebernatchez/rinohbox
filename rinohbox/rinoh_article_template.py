# rst_editor_template.py
# Rinohtype document template for RST Editor PDF output.
# Subclasses rinohtype's built-in Article template, suppressing the TOC
# and configuring margins and footer. The title renders natively on page 1.

from rinoh.attribute import OverrideDefault, Var
from rinoh.dimension import CM, PT
from rinoh.templates.article import Article, ArticleBodyPageTemplate
from rinoh.template import ContentsPartTemplate
from rinoh.text import SingleStyledText


class NoTOCContentsPartTemplate(ContentsPartTemplate):
    """Contents part with no TOC — yields document body only."""

    def _flowables(self, document):
        # Skip abstract and TOC — yield only the document body
        yield from super()._flowables(document)


def make_article(footer_text=""):

    class BareArticle(Article):
        """Article template with no TOC and configurable footer."""

        contents = NoTOCContentsPartTemplate(page_number_format='number')

        page = ArticleBodyPageTemplate(
            page_size=Var('paper_size'),
            left_margin=1.5*CM,
            right_margin=1.5*CM,
            top_margin=2.0*CM,
            bottom_margin=2.0*CM,
            header_footer_distance=2*PT,
            footer_text=SingleStyledText(footer_text) if footer_text else None,
        )
        contents_page = ArticleBodyPageTemplate(base='page')

    return BareArticle


BareArticle = make_article()
