# rst_editor_template.py
# Rinohtype document template for RST Editor PDF output.
# Subclasses rinohtype's built-in Article template, suppressing the TOC
# and configuring margins and footer. The title renders natively on page 1
# (page 1's front-matter special case is bypassed — see rinohconf.py) and
# the footer is resolved per-section, per-page, rather than baked in once
# for the whole document — see SECTION_FOOTER below.

from rinoh.attribute import OverrideDefault, Var
from rinoh.dimension import CM, PT
from rinoh.templates.article import Article, ArticleBodyPageTemplate
from rinoh.template import ContentsPartTemplate
from rinoh.reference import Field, SectionFieldType


class NoTOCContentsPartTemplate(ContentsPartTemplate):
    """Contents part with no TOC — yields document body only."""

    def _flowables(self, document):
        # Skip abstract and TOC — yield only the document body
        yield from super()._flowables(document)


class SECTION_FOOTER(SectionFieldType):
    """Field type resolving to the current section's footer text.

    Mirrors rinoh's built-in SECTION_TITLE/SECTION_NUMBER: at layout time,
    container.page.get_current_section(level) hands back whichever section
    the current physical page falls inside, and this field looks up that
    section's 'footer' reference (registered via document.set_reference —
    see the Heading.prepare patch in rinohconf.py). Each page's footer is
    therefore resolved live, per page, the same way running headers already
    are — no single footer_text baked into the page template per build.
    """
    name = 'section footer'
    reference_type = 'footer'


def make_article():

    class BareArticle(Article):
        """Article template with no TOC; footer resolved per-section."""

        contents = NoTOCContentsPartTemplate(page_number_format='number')

        page = ArticleBodyPageTemplate(
            page_size=Var('paper_size'),
            left_margin=1.5*CM,
            right_margin=1.5*CM,
            top_margin=2.0*CM,
            bottom_margin=2.0*CM,
            header_footer_distance=2*PT,
            footer_text=Field(SECTION_FOOTER(1)),
        )
        contents_page = ArticleBodyPageTemplate(base='page')

    return BareArticle


BareArticle = make_article()
