# docs/conf.py

project = 'MPAS_GOCART2G_TOOLS'
copyright = '2026, flacey19'
author = 'flacey19'

# Enable MyST-Parser extension for Markdown support
extensions = [
    'myst_parser',
]

# Tell Sphinx to parse both .rst and .md files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

html_theme = 'sphinx_rtd_theme'
