"""Sphinx configuration for the wow documentation."""

from importlib.metadata import version as package_version

project = "wow"
author = "Jacob Coffee"
copyright = "2026, Jacob Coffee"
release = package_version("wow")
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_iconify",
]

source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
exclude_patterns = ["_build"]

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_default_options = {"members": True, "show-inheritance": True}
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "msgspec": ("https://msgspec.dev", None),
}

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

html_theme = "shibuya"
html_title = "wow"
html_theme_options = {"github_url": "https://github.com/SideQuest-Guild/wow-forever-sdk"}
