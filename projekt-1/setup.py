from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name='upaproject',
    version='1.0.0',
    packages=find_packages(),    
    install_requires=requirements,
    python_requires='>=3',
    entry_points={
        "console_scripts": ["upa=upaproject.cli:cli"]}
)