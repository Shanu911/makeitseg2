from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'makeitseg2'
with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

# Setting up
setup(
    name="makeitseg2",
    version=VERSION,
    author="Shanu Biswas",
    author_email="shanubiswas119@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    
    py_modules=["makeitseg2", "formats", "header"],             # Name of the python package
    package_dir={'':'makeitseg2/src'},     # Directory of the source code of the package
    install_requires=["obspy"],
    keywords=['segy', 'seismic', 'seg2', 'segy to seg2 converter', 'segy to dat file converter', 'segy to dat file converter using python' ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)