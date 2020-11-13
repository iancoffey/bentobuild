import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bentobuild",
    version="0.0.1",
    author="Ian Coffey",
    author_email="icoffey@vmware.com",
    description="Build BentoML Services into Images on K8S without requiring a Docker Daemon",
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
