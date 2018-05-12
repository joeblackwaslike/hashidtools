import re
from setuptools import setup, find_packages


with open('hashidtools/__init__.py', 'rt') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

try:
    from m2r import parse_from_file
    long_description = parse_from_file('README.md')
except ImportError:
    with open('README.md') as fd:
        long_description = fd.read()


setup(
    name='hashidtools',
    version=version,
    description='HashID based ID Toolkit.',
    long_description=long_description,
    keywords=[
        'hashid',
        'id-generation',
        'distributed',
        'zodb',
        'database',
        'datamodels',
    ],
    author='Joe Black',
    author_email='me@joeblack.nyc',
    maintainer='Joe Black',
    maintainer_email='me@joeblack.nyc',
    url='https://github.com/joeblackwaslike/hashidtools',
    download_url=(
        'https://github.com/joeblackwaslike/hashidtools/tarball/v%s' % version),
    license='MIT',
    install_requires=[
        'zope.component>=4.4.1',
        'zope.configuration>=4.1.0',
        'zope.interface>=4.5.0',
        'zope.schema>=4.5.0',
        'zope.event>=4.3.0',
        'zope.security>=4.2.2',
        'zope.intid>=4.3.0',
        'zc.intid>=2.0.0',
        'BTrees>=4.5.0',
        'attrs>=18.2.0.dev0',
        'hashids>=1.2.0',
    ],
    zip_safe=False,
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Utilities',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
