import pkg_resources

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints'
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'Asyncio Extras'
author = 'Alex Grönholm'
copyright = '2016, ' + author

v = pkg_resources.get_distribution('asyncio_extras').parsed_version
version = v.base_version
release = v.public

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
highlight_language = 'python3'
todo_include_todos = False

html_theme = 'classic'
html_static_path = ['_static']
htmlhelp_basename = 'asyncio_extrasdoc'

intersphinx_mapping = {'https://docs.python.org/3': None}
