from pathlib import Path

from setuptools import setup, find_packages


requirements_txt_path = Path(__file__).parent.absolute() / "requirements.txt"

with open(requirements_txt_path, "r") as r:
    # Continue to use requirements.txt
    # but replace superdesk-core with setuptools equivalent syntax
    # This is so we don't have to update customer repos
    requirements = [
        line.rsplit("\n", 1)[0] for line in r.readlines() if line.rsplit("\n", 1)[0] and not line.startswith("#")
    ]

setup(
    name="Newsroom-Core",
    version="2.7.0",
    description="Newsroom Core library",
    author="Sourcefabric",
    url="https://github.com/superdesk/newsroom-core",
    license="GPLv3",
    platforms=["any"],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=requirements,
    scripts=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
