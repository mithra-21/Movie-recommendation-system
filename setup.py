from setuptools import setup

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

AUTHOR_NAME = "Mithra"
SRC_REPO = 'src'
LIST_OF_REQUIREMENTS = ['streamlit']

setup (
    name=SRC_REPO,
    version='0.0.1',
    author=AUTHOR_NAME,
    author_email='mithrapsuriakanth@gmail.com',
    description='Movie recommendation webapp',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package=[SRC_REPO],
    python_requires='>=3.6',
    install_requires=LIST_OF_REQUIREMENTS
)