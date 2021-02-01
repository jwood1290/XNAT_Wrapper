# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
try:
	import m2r2
except:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "m2r2"])
	
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'XNAT Wrapper'
copyright = '2021, John Wood'
author = 'John Wood'

# The full version, including alpha/beta/rc tags
version = '0.1'
release = '0.1.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc','m2r2']

source_suffix = ['.rst', '.md']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_options = {
	'github_user': 'jwood1290',
	'github_repo': 'XNAT_Wrapper',
	'github_banner': False,
	'github_button': True,
	'github_count': False,
	'fixed_sidebar': True,
}

html_sidebars = {
   '**': ['about.html', 'localtoc.html', 'navigation.html', 'searchbox.html']
}