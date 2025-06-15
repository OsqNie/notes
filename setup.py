from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="notes-task-manager",
    version="1.0.0",
    author="Notes Task Manager",
    description="A dual-interface task and note management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/notes-task-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Text Processing :: Markup",
    ],
    install_requires=[
        "flask==2.3.3",
        "click==8.1.7",
        "python-dateutil==2.8.2",
        "markdown==3.5.1",
    ],
    entry_points={
        "console_scripts": [
            "notes=notes.cli:cli",
        ],
    },
    python_requires=">=3.8",
    keywords="task-manager, notes, cli, web-gui, productivity, todo",
)