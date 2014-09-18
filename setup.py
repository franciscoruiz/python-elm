################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2014 Francisco Ruiz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################

import os

from setuptools import find_packages
from setuptools import setup

_CURRENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))
_README_CONTENTS = open(os.path.join(_CURRENT_DIR_PATH, "README.txt")).read()
_VERSION = \
    open(os.path.join(_CURRENT_DIR_PATH, "VERSION.txt")).readline().rstrip()


setup(
    name="python-elm",
    version=_VERSION,
    description="Python library to communicate with a vehicle's PCM "
        "(aka ECU) via an ELM327-like device",
    long_description=_README_CONTENTS,
    classifiers=[
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 2.7",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords=["OBDII", "ELM327", "PCM"],
    author="Francisco Ruiz",
    url="https://github.com/franciscoruiz/python-elm",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "pyserial>=2.7",
        ],
    test_suite="nose.collector",
    )
