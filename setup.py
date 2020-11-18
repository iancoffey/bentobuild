import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

version_file = open(os.path.join('./bentobuild/version.txt'))
version = version_file.read().strip()

setuptools.setup(
    name="bentobuild",
    version=version,
    author="Ian Coffey",
    author_email="icoffey@vmware.com",
    description="Build BentoML Services into Images on K8S",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iancoffey/bentoml-builder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
