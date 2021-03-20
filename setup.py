#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

deps = { 
    'hyp_py_tools': [
    ],
}

install_requires =  deps['hyp_py_tools']

setup(
    name='hyp-py-tools',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='0.1.0',
    description='Tools for python',
    long_description_markdown_filename='README.rst',
    author='Tommy Mckinnon',
    author_email='admin@hyperevo.com',
    url='https://github.com/hyperevo/hyp-py-tools',
    include_package_data=True,
    py_modules=['hyp_py_tools'],
    install_requires=install_requires,
    extras_require=deps,
    setup_requires=['setuptools-markdown'],
    license='MIT',
    zip_safe=False,
    keywords='hyperevo python tools',
    packages=find_packages(include=["hyp_py_tools"],
                           exclude=["tests"]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
)
