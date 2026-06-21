# rst_editor_template.py
# Rinohtype document template for RST Editor PDF output.
# Subclasses rinohtype's built-in Article template, suppressing the TOC
# and configuring margins and footer. The title renders natively on page 1
# (page 1's front-matter special case is bypassed — see rinohconf.py) and
# the footer is resolved per-section, per-page, rather than baked in once
# for the whole document — see SECTION_FOOTER below. Section numbering is
# turned off for both the in-flow heading (via a stylesheet override) and
# the running page header (via a header_text override) — see UNNUMBERED
# and the page= configuration in make_article below.

from rinoh.attribute import OverrideDefault, Var
from rinoh.dimension import CM, PT
from rinoh.templates.article import Article, ArticleBodyPageTemplate
from rinoh.template import ContentsPartTemplate
from rinoh.reference import Field, SectionFieldType, SECTION_TITLE
from rinoh.stylesheets import sphinx_article, sphinx
from rinoh.structure import HeadingStyle
from rinoh.style import StyleSheet


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


# UNNUMBERED: override 'heading level 1' (defined in the base 'sphinx'
# stylesheet, not 'sphinx_article' itself) so the in-flow article heading
# renders without a leading section number. We copy the existing entry's
# attributes rather than chaining base='heading level 1' — pointing an
# override's base string at its own entry name self-references and recurses
# forever in rinoh's lookup, since base (as a string) means "look up this
# other name in the same stylesheet," not "the entry this one replaces."
_heading_level_1_overrides = dict(sphinx['heading level 1'])
_heading_level_1_overrides['number_format'] = None

UNNUMBERED = StyleSheet('rst_editor_unnumbered', base=sphinx_article)
UNNUMBERED['heading level 1'] = HeadingStyle(**_heading_level_1_overrides)


def make_article():

    class BareArticle(Article):
        """Article template with no TOC; unnumbered headings/footers."""

        stylesheet = OverrideDefault(UNNUMBERED)
        contents = NoTOCContentsPartTemplate(page_number_format='number')

        page = ArticleBodyPageTemplate(
            page_size=Var('paper_size'),
            left_margin=1.5*CM,
            right_margin=1.5*CM,
            top_margin=2.0*CM,
            bottom_margin=2.0*CM,
            header_footer_distance=2*PT,
            header_text=Field(SECTION_TITLE(1)),
            footer_text=Field(SECTION_FOOTER(1)),
        )
        contents_page = ArticleBodyPageTemplate(base='page')

    return BareArticle


BareArticle = make_article()
