import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from rinoh_article_template import make_article

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

# Suppress subtitle and author at render time
from rinoh.templates.article import ArticleBodyPage
_original_get = ArticleBodyPage.get_header_footer_contenttop

def _patched_get(self):
    self.document.metadata.pop('subtitle', None)
    self.document.metadata.pop('author', None)
    return _original_get(self)

ArticleBodyPage.get_header_footer_contenttop = _patched_get


def extract_metadata(app, doctree):
    from docutils import nodes

    docname = app.env.docname

    # Strip .. footer:: nodes from every doctree (index and each included
    # article) so stray footer text never leaks into the rendered body.
    # Only the master doc's title/footer should drive rinoh_documents —
    # doctree-read fires once per document, and without this guard the
    # last-processed article silently overwrites the title page.
    footer_text = ""
    for node in doctree.traverse(nodes.footer):
        footer_text = node.astext()
        node.parent.remove(node)
        break

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
            "template": make_article(footer_text),
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
