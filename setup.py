import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.38'
DESCRIPTION = 'a python package for ths data '
LONG_DESCRIPTION = ' a python package for ths data  '

# Setting up
setup(
    name="thsdata",
    version=VERSION,
    author="",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(where='.', exclude=(), include=('*',)),
    include_package_data=True,
    install_requires=[],
    keywords=['python', 'thsdata'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    install_package_data=True,
    package_data={
        'thsdata': ['*.so', '*.h', '*'],
    },
)
