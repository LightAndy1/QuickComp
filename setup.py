from setuptools import setup, find_packages

setup(
    name="QuickComp",  # Replace with your package name
    version="1.0.0",  # This version will be bumped by your GitHub Action
    packages=find_packages(),  # Automatically find your package and sub-packages
    include_package_data=True,  # Include other files specified in MANIFEST.in
)
