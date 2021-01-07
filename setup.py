from setuptools import setup, find_packages


requirements = (
    'Babel>=2.5.3,<3.0',
    'WTForms==2.2.1',
    'flask-webpack>=0.1.0,<0.2',
    'Flask-WTF>=0.14.2,<0.15',
    'flask-limiter>=0.9.5.1,<0.9.6',
    'Flask-Caching>=1.9.0',
    'flask_pymongo>=0.5.2,<1.0',
    'honcho>=1.0.1',
    'gunicorn>=19.7.1',
    'icalendar>=4.0.3,<4.1',
    'PyRTF3>=0.47.5',
    'xhtml2pdf>=0.2.4',
    'superdesk-core==2.0.10',
    # dependency_links was deprecated
    'superdesk-planning@https://github.com/superdesk/superdesk-planning/archive/release/2.0.1.zip'
)

dev_requirements = (
    'flake8',
    'sphinx',
    'sphinx-autobuild',
    'pytest==3.10.0',
    'pytest-cov==2.6.1',
    'pytest-mock==1.10.1',
    'responses>=0.10.6,<0.11',
    'httmock',
    'wooper'
)

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
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements
    },
    scripts=['manage.py'],
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
