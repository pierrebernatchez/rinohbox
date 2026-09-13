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
from rinoh.reference import Field, SectionFieldType, SECTION_TITLE, PAGE_NUMBER
from rinoh.stylesheets import sphinx_article, sphinx
from rinoh.structure import HeadingStyle
from rinoh.style import StyleSheet
from rinoh.flowable import GroupedFlowablesStyle, GroupedFlowables
from rinoh.paragraph import Paragraph, ParagraphStyle
from rinoh.text import Tab, StyledText, TextStyle
from rinoh.math import Equation, DisplayEquation, EquationStyle
from rinoh.color import RED


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

# 'keeptogether group': the style rinohconf.py's Container.build_flowable
# patch applies to a `.. container:: keeptogether` block. same_page="try
# to keep all this group's flowables on one page, moving the whole group
# to the next page rather than splitting it, if it doesn't fit" -- a
# real rinoh capability (rinoh.flowable.GroupedFlowablesStyle) that had
# no RST-level directive wired up to it before this.
#
# Two registrations are both required, and this took direct debugging
# (temporary print-instrumentation of rinoh's own GroupedFlowables.render,
# not guessing) to work out: setting UNNUMBERED['keeptogether group'] = ...
# alone stores a VALUE under that name, but nothing tells rinoh's style
# *matcher* (a separate registry from the stylesheet's own values) that a
# flowable with .style == 'keeptogether group' should resolve to it --
# without the matcher entry, get_style('same_page', ...) silently falls
# through to the attribute's default (False) with no error. The matcher
# entry is what rinoh's own built-in named groups (e.g. 'block quote',
# 'example' -- see rinoh/stylesheets/matcher.py) all rely on via this
# exact same GroupedFlowables.like(name) pattern.
UNNUMBERED.matcher['keeptogether group'] = GroupedFlowables.like('keeptogether group')
UNNUMBERED['keeptogether group'] = GroupedFlowablesStyle(same_page=True)

# 'keep with next': the style rinohconf.py's Paragraph.build_flowable
# patch applies to a paragraph immediately preceded by `.. rst-class::
# keepwithnext` (Sphinx's alias for docutils' built-in "class"
# directive, tags just the one next element). keep_with_next=True is a
# plain FlowableStyle attribute ("keep this flowable and the next on the
# same page") -- narrower than 'keeptogether group' above: this only
# pins one flowable to its immediate successor, for the common case of a
# label (e.g. "a)", "Example 1:") left alone at the bottom of a page
# while its content starts fresh on the next one.
#
# base='body' is required, not optional: ParagraphStyle's own base
# defaults to None (no inheritance at all), so without it this style
# would resolve every other attribute -- space above/below, font, indent
# -- to the bare class default instead of matching an ordinary
# paragraph. Confirmed by direct testing: omitting base collapsed the
# spacing above the labeled paragraph to ~0, visibly crowding it against
# the previous paragraph. 'body' is rinoh's own built-in name for a
# plain, unstyled paragraph (rinoh/stylesheets/matcher.py:
# matcher('body', Paragraph)) -- the same fallback every other ordinary
# paragraph in the document already resolves to.
UNNUMBERED.matcher['keep with next'] = Paragraph.like('keep with next')
UNNUMBERED['keep with next'] = ParagraphStyle(base='body', keep_with_next=True)

# 'solution equation': the style rinohconf.py's Math_Block/Math
# build_flowable/build_styled_text patches apply to a `.. math:: :class:
# solution` block (inline `:math:` role classing not wired up the same
# way docutils roles don't carry an inline :class: option the way block
# directives do -- block-level only for this spike). font_color is a
# real, already-existing EquationStyle attribute (rinoh/math.py) -- rinoh
# just never had anything set it to non-black before this. Two matcher
# entries (one per node type) both resolve to the one style value --
# ClassSelectors don't support `|` to combine into a single registration.
# Both the inline and block cases end up as `Equation` instances (the
# block case wraps one inside a DisplayEquation, but the *inner*
# Equation is what actually needs the style -- see the
# _RedDisplayEquation comment in rinohconf.py). The `.like(style_name)`
# argument must match the literal string passed as `style=` when the
# object is constructed -- ClassSelector.match checks `styled.style ==
# self.style_name` -- these two strings not matching (a real bug hit
# and fixed here) is why the first attempt silently rendered black.
# `+Equation.like(...)` (not a bare `Equation.like(...)`) for the same
# reason 'solution text'/'solution paragraph' below need it: a bare
# ClassSelector's priority is always 0, and rinoh has other built-in
# structural rules (e.g. 'table first column paragraph' -- discovered
# the hard way, see the 'solution paragraph' comment below) that also
# resolve at priority 0 but with a higher klass score, silently winning
# over ours whenever an "added" answer happens to land in one of those
# structural positions. `+` (Selector.__pos__ -> .pri(1)) guarantees our
# rule outranks *any* priority-0 competitor regardless of klass.
_solution_equation_style = EquationStyle(font_color=RED)
UNNUMBERED.matcher['solution equation inline'] = +Equation.like('solution equation inline')
UNNUMBERED['solution equation inline'] = _solution_equation_style

# The block case can't use a bare ClassSelector like the inline one above:
# rinoh's own built-in 'math block equation' matcher (rinoh/stylesheets/
# matcher.py) is a context/descendant selector chain --
# `SelectorByName('math block paragraph') / ... / Equation` -- and
# 'math block paragraph' is itself `'math block' / +Paragraph`, where
# `+Paragraph` (Selector.__pos__ -> .pri(1)) is where that built-in rule's
# Specificity.priority=1 actually comes from. Specificity compares
# `priority` before every other field, so a plain `Equation.like(...)`
# ClassSelector (priority always 0) can never win against it regardless of
# style-name specificity, no matter how the two rules compare elsewhere.
#
# Reusing `SelectorByName('math block paragraph')` directly doesn't work
# here: UNNUMBERED.matcher is its own fresh StyledMatcher (not the same
# instance rinoh's built-in matcher.py populates), and StyledMatcher.
# __setitem__ only registers a selector once every name it *references* is
# already defined in that *same* matcher instance -- otherwise it's parked
# in self._pending forever and never actually added. So instead the same
# chain shape is built directly from the classes themselves (DisplayEquation
# / +Paragraph / ... / Equation), sidestepping by-name lookup entirely.
# This reproduces the built-in rule's priority=1, and the final
# `Equation.like('solution equation block')` link then wins the tiebreak on
# the very next Specificity field (style_match=1 vs. the built-in's 0).
UNNUMBERED.matcher['solution equation block'] = (
    DisplayEquation / +Paragraph / ... / Equation.like('solution equation block')
)
UNNUMBERED['solution equation block'] = _solution_equation_style

# 'solution text': red for plain (non-math) "added to make it a
# solution" content -- table-cell answers, short words ("Yes"/"No"/
# "Even"), bare numbers, etc. -- tagged via `` :sol:`...` `` (a plain
# docutils custom role with no base role, defined once in rinohconf.py's
# rst_prolog; see that file's Design F comment). Unlike Equation above,
# this needs no rinohconf.py monkeypatch at all: rinoh's generic
# DocutilsInlineNode.styled_text() (rinoh/frontend/rst/__init__.py)
# already copies a node's docutils `classes` onto the resulting
# StyledText's own `.classes` list for every node type that doesn't
# override styled_text/build_flowable itself (unlike Math/Math_Block,
# which is exactly why those two needed the Design E patch).
#
# `+StyledText.like(...)`, not bare: see the 'solution paragraph' comment
# below for the exact bug this avoids (a same-priority, higher-klass
# built-in rule silently winning for certain structural positions).
UNNUMBERED.matcher['solution text'] = +StyledText.like(has_class='solution')
UNNUMBERED['solution text'] = TextStyle(font_color=RED)

# 'solution paragraph': whole-paragraph (or whole table-cell, which
# docutils wraps in a paragraph the same way) version of the above, for
# the common case where an ENTIRE answer -- not just one word or one
# inline math fragment -- is "added" content, e.g. a full worked-answer
# sentence in a list-table cell. `.. rst-class:: solution` immediately
# before the paragraph (same directive Design D's 'keep with next'
# uses) tags the whole thing at once, including any *plain* (unclassed)
# `:math:` nested inside it -- no need to individually mark every word
# with :sol: or switch every nested :math: to :solmath:. This relies on
# StyledText/Equation.fallback_to_parent already returning True for
# font_color (rinoh/text.py, rinoh/math.py): a child with no more
# specific color match of its own climbs to its parent flowable (this
# Paragraph) and re-resolves there, inheriting whatever font_color the
# paragraph itself resolved to. base='body' is required for the same
# reason 'keep with next' above needs it -- ParagraphStyle has no
# default base, so omitting it would blank out ordinary paragraph
# spacing/alignment, not just add color.
#
# **Real bug hit and fixed here:** a bare `Paragraph.like(has_class=
# 'solution')` silently fails to turn red specifically for a paragraph
# that's the FIRST cell in a list-table row -- found via a 2-cell test
# table where the second cell worked and the first didn't, despite
# identical RST. Root cause (confirmed via the same debug-print
# technique used for the math priority-tier bug): rinoh has a built-in
# 'table first column paragraph' style that also matches at
# `Specificity(priority=0, ..., attributes=1, klass=8)` -- same
# priority and attributes-match count as ours, but a higher klass score
# (it's a context/descendant selector under the hood, like 'math block
# equation' was), so it wins the tiebreak and is asked to resolve
# font_color instead of ours -- and since IT doesn't set font_color
# either, its own base chain resolves to the plain default (black)
# *without* ever falling through to try our rule next. `+Paragraph...`
# (priority=1) sidesteps this the same way Design E's block-math fix
# did: our rule now outranks *any* priority-0 competitor regardless of
# klass, not just this one specific built-in.
UNNUMBERED.matcher['solution paragraph'] = +Paragraph.like(has_class='solution')
UNNUMBERED['solution paragraph'] = ParagraphStyle(base='body', font_color=RED)


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
            footer_text=Field(SECTION_FOOTER(1)) + Tab() + Field(PAGE_NUMBER),
        )
        contents_page = ArticleBodyPageTemplate(base='page')

    return BareArticle


BareArticle = make_article()
