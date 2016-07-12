from setuptools import setup
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='passepartout-package',

    version='1.0.0',

    description='Python script to generate Debian packages from Mille feuilles, Clin d\'Oeil and New World DVDs',
    long_description=long_description,

    url='http://www.lernstick.ch/',

    # Author details
    author='Lernstick Project',
    author_email='lernstick.ph@fhnw.ch',

    # Choose your license
    license='GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='debian passepartout package',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['passepartout'],
    package_data={'passepartout': ['templates/compat',
                                   'templates/control',
                                   'templates/menu.desktop',
                                   'templates/menu.directory',
                                   'templates/merge.menu',
                                   'templates/rules',
                                   'templates/source/*']},

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['PyYAML', 'Jinja2'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
          'passepartout-package=passepartout.shell:passepartout_package',
        ],
    },
)
