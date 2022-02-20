from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="registryspy",
    version="1.0.1",
    author="Andy Smith",
    description="Cross-platform Windows Registry browser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andyjsmith/Registry-Spy",
    keywords=[
        "registry",
        "forensics",
        "windows forensics",
        "forensics tools"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: X11 Applications :: Qt",
        "Environment :: MacOS X"
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PySide6",
        "python-registry"
    ],
    entry_points={
        "console_scripts": ["registryspy=registryspy.registryspy:main"],
    },
    include_package_data=True
)
