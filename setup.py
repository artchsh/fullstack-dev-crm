from setuptools import setup, find_packages
import os
import sys

# Add src to path to import version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from __init__ import __version__, __author__, __email__, __description__

# Read the contents of README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="client-data-manager",
    version=__version__,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "cryptography>=41.0.0",
        "sqlalchemy>=2.0.0",
        "ttkbootstrap>=1.14.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "client-data-manager=src.main:main",
        ],
    },
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/artchsh/fullstack-dev-crm",
    project_urls={
        "Bug Reports": "https://github.com/artchsh/fullstack-dev-crm/issues",
        "Source": "https://github.com/artchsh/fullstack-dev-crm",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Environment :: X11 Applications :: Qt",
        "Topic :: Database :: Front-Ends",
    ],
    keywords="client management, database, hosting, crm, desktop application",
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)