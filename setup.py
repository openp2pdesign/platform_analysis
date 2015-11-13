from distutils.core import setup
setup(
    name='repoSNA',
    packages=['repoSNA'],
    install_requires=[
        "kitchen",
        "requests",
        "mwparserfromhell",
        "simplemediawiki",
        "wsgiref"
    ],
    version='0.11',
    description='Python library for Social Network Analysis of Git, Hg, SVN, GitHub, BitBucket repositories',
    author='Massimo Menichinelli',
    author_email='info@openp2pdesign.org',
    url='https://github.com/openp2pdesign/repoSNA',
    download_url='https://github.com/openp2pdesign/repoSNA/releases/tag/v0.1',
    keywords=['Git', 'Hg', 'Mercurial', 'SVN', 'Subversion',
              'GitHub', 'BitBucket', 'Social Network Analysis', 'SNA'],
    classifiers=["Development Status :: 3 - Alpha",
                 "Topic :: Utilities",
                 "Environment :: Web Environment",
                 "Operating System :: OS Independent",
                 "Intended Audience :: Science/Research",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2",
                 "Programming Language :: Python :: 2.7",
                 "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)", ],
)
