from setuptools import setup, find_packages

setup(
    name="MyTkinterApp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "tkinter",
    ],
    entry_points={
        "console_scripts": [
            "my-tkinter-app=main:main",
        ],
    },
)
