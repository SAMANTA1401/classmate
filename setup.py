import setuptools

with open('README.md', "r", encoding="utf-8") as f:
    long_description = f.read()


__versio__ = "0.0.1"

REPO_NAME = "classmate"
AUTHOR_USER_NAME = "SAMANTA1401"
SRC_REPO = "src"

setuptools.setup(
    name=REPO_NAME,
    version=__versio__,
    author=AUTHOR_USER_NAME,
    description="A small python package for tutorengine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    packages=setuptools.find_packages()
)