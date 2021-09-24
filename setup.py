from pathlib import Path

from setuptools import setup, find_packages


# Disable this for now, until the fix for `feedparser` in core is released
# requirements_txt_path = Path(__file__).parent.absolute() / 'requirements.txt'
#
# with open(requirements_txt_path, 'r') as r:
#     requirements = [line.rsplit('\n', 1)[0] for line in r.readlines()]

setup(
    name='Newsroom-Core',
    version='1.0',
    description='Newsroom Core library',
    author='Sourcefabric',
    url='https://github.com/superdesk/newsroom-core',
    license='GPLv3',
    platforms=['any'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    # install_requires=[],
    scripts=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
