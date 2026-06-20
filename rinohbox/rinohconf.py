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
