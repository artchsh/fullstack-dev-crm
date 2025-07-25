from setuptools import setup, find_packages

setup(
    name="client-data-manager",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tkinter",
        "sqlite3",
    ],
    entry_points={
        "console_scripts": [
            "client-data-manager=main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A GUI application to manage client data securely.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/client-data-manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)