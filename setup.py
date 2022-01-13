import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="data_helpers",
    version="0.0.18",
    author="sbland",
    author_email="sblandcouk@gmail.com",
    description="A set of helpers for working with various datatypes",
    long_description=long_description,
    install_requires=[
        'numpy'
    ],
    setup_requires=[
        'wheel',
        'pytest-cov',
        'pytest-runner',
        'snapshottest',
        'deprecated'
    ],
    tests_require=['pytest', 'numpy', 'pytest-benchmark'],
    extras_require={'test': ['pytest', 'numpy']},
    packages=setuptools.find_packages(),
    package_dir={'data_helpers': 'data_helpers'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
