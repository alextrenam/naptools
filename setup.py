# This file sets up the package to be callable system-wide

from setuptools import setup

setup(name="naptools",
      version="0.6.0",
      packages=["naptools"],
      package_dir={"":"src"}
      )
