# Configuration file for the Sphinx documentation builder.
#
# The package must be installed in the docs environment (e.g. `uv sync`),
# so autodoc imports it like any user would. No sys.path manipulation needed.

from importlib.metadata import version as _package_version

# -- Project information ------------------------------------------------------

project = "VolsegTools"
copyright = "2026, Mol*"
author = "Mol*"

release = _package_version("volsegtools")  # full version, e.g. "0.2.5"
version = ".".join(release.split(".")[:2])  # short version, e.g. "0.2"

# -- General configuration ----------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_autodoc_typehints",  # must come after napoleon
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

# Report every unresolved reference (same as passing -n to sphinx-build).
nitpicky = True
nitpick_ignore = [
    # trimesh does not publish a Sphinx inventory.
    ("py:class", "trimesh.Trimesh"),
    ("py:class", "trimesh.base.Trimesh"),
]
nitpick_ignore_regex = [
    # TypeVars cannot have their __module__ rewritten.
    ("py:class", r".*\bTData"),
    ("py:class", r".*\bTData"),
    ("py:class", r"pydantic\..*"),
    ("py:class", r"zarr\..*"),
]

# -- autodoc / autosummary ----------------------------------------------------

autosummary_generate = True
autosummary_ignore_module_all = False  # __all__ defines the public API

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
    "exclude-members": "__weakref__, __dict__, __abstractmethods__, __protocol_attrs__",
}
autodoc_preserve_defaults = True

# -- Type hints (annotations are the single source of truth) -----------------

typehints_use_signature = True
typehints_use_signature_return = True
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
typehints_use_rtype = False

# -- napoleon (NumPy-style docstrings) ----------------------------------------

napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_use_rtype = False
napoleon_preprocess_types = False

# -- intersphinx --------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "dask": ("https://docs.dask.org/en/stable/", None),
}
intersphinx_disabled_domains = ["std"]

# -- HTML output --------------------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_favicon = "_static/favicon.svg"

html_theme_options = {
    "navbar_align": "left",
    "logo": {
        "text": "VolsegTools",
        "image_light": "_static/favicon.svg",
        "image_dark": "_static/favicon.svg",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/molstar/volsegtools",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
        {
            "name": "Mol*",
            "url": "https://molstar.org/",
            "icon": "_static/molstar_favicon.svg",
            "type": "local",
        },
        {
            "name": "PyPI Package",
            "url": "https://pypi.org/project/volsegtools/",
            "icon": "_static/pypi_icon.svg",
            "type": "local",
        },
        # TODO: add the Conda link once the package is published there.
        # {
        #     "name": "Conda Package",
        #     "url": "https://anaconda.org/<channel>/volsegtools",
        #     "icon": "_static/conda_icon.svg",
        #     "type": "local",
        # },
    ],
}

# -- EPUB output --------------------------------------------------------------

epub_show_urls = "footnote"
