import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dcml-musical-pitch-types", # Replace with your own username
    version="0.0.1",
    author="Robert Lieck",
    description="musically meaningful pitch types",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DCMLab/pitchtypes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

