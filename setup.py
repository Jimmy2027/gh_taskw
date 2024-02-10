#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["Click>=7.0", "pandas>=2.1", "loguru>=0.5.3"]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Hendrik Klug",
    author_email="hendrik.klug@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Convert GitHub notifications to taskwarrior tasks",
    entry_points={
        "console_scripts": ["gh_taskw=gh_taskw.cli:main"],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n",
    include_package_data=True,
    keywords="gh_taskw",
    name="gh_taskw",
    packages=find_packages(include=["gh_taskw", "gh_taskw.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/Jimmy2027/gh_taskw",
    version="0.1.0",
    zip_safe=False,
)
