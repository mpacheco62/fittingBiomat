import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fittingBiomat",
    version="0.0.6",
    author="Matias Pacheco, Andres Utrera",
    author_email="Matias.Pacheco.A@gmail.com, Andres.Utrera@usach.cl",
    description="Fitting parameters for inhouse FEM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mpacheco62/fittingBiomat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3',
    install_requires=["scipy", "intervul", "numpy"],
)