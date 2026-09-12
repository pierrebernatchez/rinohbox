import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from rinoh_article_template import make_article
from rinoh.frontend.sphinx.util import fully_qualified_id

project   = ""
author    = ""
copyright = ""
release   = ""
version   = ""

suppress_warnings = ["config.cache"]

extensions = ["sphinx.ext.mathjax", "rst_directives"]

mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

source_suffix    = ".rst"
master_doc       = "index"
exclude_patterns = ["_build"]

html_theme = "alabaster"

# Design B storage: each article's footer text, captured at doctree-read
# time, keyed by the *fully-qualified* section id rinoh will eventually
# assign that section's Heading once index.rst's toctree gets merged into
# one combined doctree (rinoh.frontend.sphinx.RinohTreePreprocessor rewrites
# every section id to this same '%docname#id' form before rinoh objects are
# built from it — see fully_qualified_id). Populated in extract_metadata
# below; consumed by the Heading.prepare patch further down, which is the
# point where a rinoh Section object's final (already-fully-qualified) id
# is first available to register against document.set_reference.
_section_footers = {}

# Design A: bypass rinoh's page-1 front-matter special case.
# ArticleBodyPage.get_header_footer_contenttop normally branches on
# self.number == 1 to render a title block plus title_page_header_text/
# title_page_footer_text instead of the normal header_text/footer_text
# path used on every other page. We never set title_page_footer_text, so
# page 1 currently has no footer at all. Rather than populate that
# separate option, we drop the branch: page 1 now goes through the exact
# same get_header_footer_contenttop as page 2+ (BodyPage's, two levels up
# the MRO), so the per-section SECTION_FOOTER field resolves there too,
# and the article's own title becomes an ordinary in-flow heading rather
# than special title-page treatment.
from rinoh.template import BodyPage
from rinoh.templates.article import ArticleBodyPage

def _patched_get(self):
    self.document.metadata.pop('subtitle', None)
    self.document.metadata.pop('author', None)
    return BodyPage.get_header_footer_contenttop(self)

ArticleBodyPage.get_header_footer_contenttop = _patched_get


# Design B: register each section's footer text with the rinoh document
# the first time that section's Heading is prepared for layout. By this
# point self.section.get_id(document) returns the fully-qualified
# '%docname#id' string (Sphinx's RinohTreePreprocessor has already rewritten
# it), which is exactly the key extract_metadata stores footer text under —
# so no separate docname bookkeeping is needed here, just a dict lookup.
from rinoh.structure import Heading
_original_heading_prepare = Heading.prepare

def _patched_heading_prepare(self, container):
    _original_heading_prepare(self, container)
    document = container.document
    section_id = self.section.get_id(document, create=False)
    if section_id in _section_footers:
        document.set_reference(section_id, 'footer', _section_footers[section_id])

Heading.prepare = _patched_heading_prepare


# Design C: `.. container:: keeptogether` keeps its contents on a single
# page (or moves the whole block to the next page if it doesn't fit),
# instead of letting rinoh split it wherever the page boundary happens to
# land. docutils' built-in "container" directive already tags its node
# with whatever class name follows it; rinoh's own RST frontend
# (Container.build_flowable, rinoh/frontend/rst/nodes.py) already
# branches on specific class names ('literal-block-wrapper', 'out-of-
# line') to build a different flowable type for each — this patch adds
# one more branch the same way, so it stays consistent with how rinoh
# itself already extends this method, without editing rinoh's own
# installed package source (not ours to maintain) or the separate
# rst_directives package (a different project's work in progress).
# same_page (rinoh.flowable.GroupedFlowablesStyle) is a real, existing
# rinoh capability ("keep all flowables on a single page, if possible")
# that was simply never wired up to any RST-level directive before this.
from rinoh.frontend.rst.nodes import Container
import rinoh.flowable as rf

_original_container_build_flowable = Container.build_flowable

def _patched_container_build_flowable(self, style=None, **kwargs):
    classes = self.get('classes')
    if 'keeptogether' in classes:
        return rf.StaticGroupedFlowables(self.children_flowables(),
                                          style='keeptogether group',
                                          **kwargs)
    return _original_container_build_flowable(self, style, **kwargs)

Container.build_flowable = _patched_container_build_flowable


# Design D: `.. rst-class:: keepwithnext` immediately before a paragraph
# (Sphinx's own alias for docutils' built-in "class" directive -- tags
# the SINGLE next element with the given class, no dependency on
# rst_directives) glues that paragraph to whatever flowable comes right
# after it, so a label like "a)" or "Example 1:" is never left alone at
# the bottom of a page with its content starting fresh on the next one.
# Narrower than Design C's keeptogether (which holds a whole block
# together): this only pins one flowable to its immediate successor.
# Same reasoning as Design C for why this is a patch here rather than a
# rinoh/rst_directives change -- see that design's comment above.
#
# MUST use `rst-class`, not the bare docutils spelling `class`: Sphinx
# loads the Python domain by default, and that domain claims the
# unprefixed `class` directive name for documenting Python classes (a
# `py:class` shortcut) -- confirmed by direct testing (a bare `..
# class:: keepwithnext` silently rendered as a literal "class
# keepwithnext" signature block instead of tagging the next paragraph,
# with the pending-node class-transform never running at all). Sphinx
# registers `rst-class` (sphinx/directives/other.py) as an alias to
# docutils' original, unshadowed directive specifically to route around
# this collision.
from rinoh.frontend.rst.nodes import Paragraph as RSTParagraphNode
from rinoh.paragraph import Paragraph as RinohParagraph

_original_paragraph_build_flowable = RSTParagraphNode.build_flowable

def _patched_paragraph_build_flowable(self):
    classes = self.get('classes')
    if 'keepwithnext' in classes:
        return RinohParagraph(self.process_content(), style='keep with next')
    return _original_paragraph_build_flowable(self)

RSTParagraphNode.build_flowable = _patched_paragraph_build_flowable


# Design E: `.. math:: :class: solution` SHOULD render in red -- SPIKE
# for "added-to-make-it-a-solution content should be red" (see
# project_solutions_red_text_convention memory). **STATUS: NOT YET
# WORKING, root cause identified, needs more work than a spike covers.**
#
# Two real bugs were found and fixed getting this far:
# 1. rinoh's own RST frontend (rinoh/frontend/rst/nodes.py:
#    Math_Block.build_flowable, Math.build_flowable) hardcodes
#    `rt.DisplayEquation(self.text)` / `rt.Equation(self.text)` with no
#    style argument at all -- docutils' standard `:class:` option on a
#    math directive is silently dropped, never reaching rinoh's
#    Equation/DisplayEquation constructors. Fixed the same way Design
#    C/D above do: check for a class docutils already parses for us, and
#    pass a `style=` name through explicitly.
# 2. `DisplayEquation.__init__` (rinoh/math.py) *also* hardcodes its
#    inner `Equation(latex_equation, inline=False)` with no style
#    argument -- a style passed to DisplayEquation itself only reaches
#    the outer LabeledFlowable wrapper (no font_color attribute there),
#    never the inner Equation that actually renders glyphs. Worked
#    around via `_RedDisplayEquation` below, which bypasses
#    DisplayEquation.__init__ entirely to construct the inner Equation
#    with the right style directly.
#
# **The actual blocker, found via direct instrumentation of
# `StyleSheet._get_value_lookup`/`Document.get_matches`:** even once the
# custom Equation correctly carries `style='solution equation block'`
# and a matching stylesheet entry with `font_color=RED` exists, rinoh's
# *built-in* `'math block equation'` selector (rinoh/stylesheets/
# matcher.py, a context/descendant selector chain via `SelectorByName(...)
# / ... / Equation`) always wins the match, because rinoh's Specificity
# tuple starts with a `priority` field, and context/descendant selectors
# get `priority=1` unconditionally -- a plain `Equation.like(style_name)`
# ClassSelector (what's used below) can only ever produce `priority=0`,
# so it *always* loses regardless of how specific the style-name/class
# match is on the later tuple positions. This is an architectural
# precedence tier in rinoh's own selector system, not a typo to fix.
# Confirmed via debug prints showing `Specificity(priority=1, ...,
# klass=5)` beating `Specificity(priority=0, ..., style=1, klass=2)`
# every time. **Next step for whoever picks this up:** construct a
# context/descendant selector of the same shape as the built-in one
# (rather than a bare `Equation.like(...)` ClassSelector) so the custom
# rule also gets `priority=1`, letting the `style=1` tiebreak actually
# decide it.
#
# The inline `Math.build_styled_text` patch below is additionally NOT
# reachable via any known plain-RST syntax yet even once the above is
# fixed: docutils' inline `:math:` role has no `:class:`-equivalent way
# to tag individual instances the way a block directive's `:class:`
# option does, so `self.get('classes')` on an inline math node is always
# empty today. Wiring up a real "some of this inline math should be red"
# case would need a genuinely new mechanism (e.g. a custom Sphinx role).
from rinoh.frontend.rst.nodes import Math_Block, Math as RSTMathNode
from rinoh.math import DisplayEquation, Equation, EquationLabel
from rinoh.paragraph import Paragraph as RinohParagraphForMath
from rinoh.text import Tab as MathTab


class _RedDisplayEquation(DisplayEquation):
    """DisplayEquation whose inner Equation gets a style, unlike the
    base class. rinoh/math.py's DisplayEquation.__init__ hardcodes
    `Equation(latex_equation, inline=False)` with no style argument --
    a style passed to DisplayEquation itself only affects the outer
    LabeledFlowable wrapper, which has no font_color attribute, so it's
    silently inert for controlling the rendered glyph color (confirmed
    by direct testing: the outer style was applied and had zero visual
    effect). Subclassing (rather than duplicating the label/category
    wiring by hand) keeps `category = 'equation'` and
    `EquationLabel.referenceable` (-> self.parent) working, which a
    bare `LabeledFlowable(...)` substitute does not (raises
    AttributeError: 'LabeledFlowable' object has no attribute
    'category' at render time).
    """

    def __init__(self, latex_equation, equation_style, **kwargs):
        # Deliberately does NOT call super().__init__ -- that's exactly
        # the code path being replaced. Goes straight to
        # LabeledFlowable.__init__ (DisplayEquation's own parent).
        paragraph = RinohParagraphForMath(
            MathTab() + Equation(latex_equation, inline=False,
                                  style=equation_style))
        label = EquationLabel()
        super(DisplayEquation, self).__init__(label, paragraph, **kwargs)


_original_math_block_build_flowable = Math_Block.build_flowable

def _patched_math_block_build_flowable(self):
    classes = self.get('classes')
    if 'solution' in classes:
        return _RedDisplayEquation(self.text, 'solution equation block')
    return _original_math_block_build_flowable(self)

Math_Block.build_flowable = _patched_math_block_build_flowable

_original_math_inline_build_styled_text = RSTMathNode.build_styled_text

def _patched_math_inline_build_styled_text(self):
    classes = self.get('classes')
    if 'solution' in classes:
        return Equation(self.text, style='solution equation inline')
    return _original_math_inline_build_styled_text(self)

RSTMathNode.build_styled_text = _patched_math_inline_build_styled_text


def extract_metadata(app, doctree):
    from docutils import nodes

    docname = app.env.docname

    # Strip .. footer:: nodes from every doctree (index and each included
    # article) so stray footer text never leaks into the rendered body.
    # Capture the text against this doc's top-level section id (fully
    # qualified the same way rinoh's Sphinx bridge will later qualify it),
    # so design B's per-section field can look it up at layout time. A doc
    # with no top-level section (e.g. index.rst itself, a content-free
    # toctree shell) has nothing to key the footer against, so its footer
    # text — if any — is simply not registered; that's fine, it has no
    # section for SECTION_FOOTER to resolve against either.
    footer_text = ""
    for node in doctree.traverse(nodes.footer):
        footer_text = node.astext()
        node.parent.remove(node)
        break

    if footer_text:
        section_id = None
        for node in doctree.traverse(nodes.section):
            section_id = node['ids'][0] if node['ids'] else None
            break
        if section_id:
            _section_footers[fully_qualified_id(docname, section_id)] = footer_text

    if docname != app.config.master_doc:
        return

    title_text = ""
    for node in doctree.traverse(nodes.title):
        title_text = node.astext()
        break

    app.config.rinoh_documents = [
        {
            "doc":      "index",
            "target":   "output",
            "title":    title_text,
            "author":   "",
            "template": make_article(),
        }
    ]


def setup(app):
    app.connect("doctree-read", extract_metadata)


rinoh_documents = [
    {
        "doc":      "index",
        "target":   "output",
        "title":    "",
        "author":   "",
        "template": make_article(),
    }
]
