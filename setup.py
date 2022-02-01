import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="nirone",
    version="0.0.1",
    scripts=["bin/nirone"],
    author="Tristan Lieberherr",
    author_email="tristan.lieberherr@heig-vd.ch",
    description="NIROne programming interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TristanLieberherr/NIROne_package",
    packages=["nirone"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pymodbus"],
)