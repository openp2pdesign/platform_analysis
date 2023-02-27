#from distutils.core import setup
from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

from distutils.core import setup
setup(
    name='platform_analysis',
    packages=['platform_analysis'],
    install_requires=[
        "decorator",
        "PyGithub",
        "networkx",
        "requests",
        "python-dateutil",
        "six",
        "splitstream",
        "xmltodict",
        "pandas",
        "datetime",
        "pydiscourse",
        "ratelimit",
        "twitter",
        "pathlib"
    ],
    version='0.31',
    description='A Python library for Social Network Analysis of online collaboration platforms and tools like Twitter, YouTube and Git, Hg, SVN, GitHub, GitLab, BitBucket repositories',
    author='Massimo Menichinelli',
    author_email='info@openp2pdesign.org',
    url='https://github.com/openp2pdesign/platform_analysis',
    download_url='https://github.com/openp2pdesign/platform_analysis/releases/tag/v0.31',
    keywords=['Git', 'Hg', 'Mercurial', 'SVN', 'Subversion',
              'GitHub', 'BitBucket', 'Twitter', 'Social Network Analysis', 'SNA'],
    classifiers=["Development Status :: 3 - Alpha",
                 "Topic :: Utilities",
                 "Environment :: Web Environment",
                 "Operating System :: OS Independent",
                 "Intended Audience :: Science/Research",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)", ],
)
