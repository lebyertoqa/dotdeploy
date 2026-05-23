"""Package setup for dotdeploy."""

from setuptools import setup, find_packages

setup(
    name="dotdeploy",
    version="0.1.0",
    description="Minimal dotfiles manager with profile switching and remote backup support.",
    author="dotdeploy contributors",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        "console_scripts": [
            "dotdeploy=dotdeploy.cli:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7",
            "pytest-cov",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
    ],
)
