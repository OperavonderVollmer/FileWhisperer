from setuptools import setup, find_packages

setup(
    name="FileWhisperer",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "pytaglib",
        "python-magic-bin",
        "pillow",
        "OperaPowerRelay @ git+https://github.com/OperavonderVollmer/OperaPowerRelay.git@v1.1.2",
    ],
    python_requires=">=3.7",
    author="Opera von der Vollmer",
    description="Script for manipulating metadata of files",
    url="https://github.com/OperavonderVollmer/FileWhisperer", 
    license="MIT",
)
