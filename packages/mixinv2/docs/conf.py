# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import subprocess
import sys
from pathlib import Path

from sphinx.ext import apidoc

# -- Path setup --------------------------------------------------------------
# Add mixinv2/src to sys.path so autodoc can import the modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MIXINv2'
copyright = '2025, Bo Yang'
author = 'Bo Yang'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx_mdinclude',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

autodoc_default_options = {
    'imported-members': True,
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'api/modules.rst']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'alabaster'
html_favicon = '_static/favicon.svg'
html_theme_options = {
    'description': 'A dependency injection framework with pytest-fixture syntax, '
                   'plus a configuration language for declarative programming.',
    'logo': 'logo.svg',
    'fixed_sidebar': True,
    'github_user': 'Atry',
    'github_repo': 'MIXINv2',
    'github_banner': True,
    'github_button': True,
    'github_type': 'watch',
    'github_count': True,
}

# -- GitHub source links (pinned to git commit) --------------------------------

_git_commit = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], text=True
).strip()

extlinks = {
    'github': (
        f'https://github.com/Atry/MIXINv2/tree/{_git_commit}/%s',
        '%s',
    ),
}


def _generate_api_docs(app: object) -> None:
    docs_directory = Path(__file__).resolve().parent
    package_directory = docs_directory.parent / "src" / "mixinv2"
    output_directory = docs_directory / "api"

    apidoc.main([
        "--implicit-namespaces",
        "-o",
        str(output_directory),
        str(package_directory),
    ])


def setup(app: object) -> None:
    app.connect("builder-inited", _generate_api_docs)
