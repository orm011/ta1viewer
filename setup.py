from setuptools import setup, find_packages

setup(
    name="ta1viewer",
    version="0.0.1",
    url="git@github.com:orm011/ta1viewer.git",
    author="Oscar Moll",
    author_email="orm@csail.mit.edu",
    description="some tools for lightweight ta1 output viz",
    packages=find_packages(where="ta1viewer"),
    install_requires=[],  # installed from pyproject.toml
    python_requires=">=3.7",
)