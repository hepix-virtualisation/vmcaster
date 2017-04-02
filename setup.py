from sys import version_info
import os
from vmcasterpub.__version__ import version
if version_info < (2, 6):
    import sys
    print ("Please use a newer version of python")
    sys.exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
	try:
            from distutils.core import setup
	except ImportError:
            from ez_setup import use_setuptools
            use_setuptools()
            from setuptools import setup, find_packages


doc_files_installdir = "/usr/share/doc/vmcaster"
cfg_files_installdir = "/etc/vmcaster"
if "VIRTUAL_ENV" in  os.environ:
    doc_files_installdir = 'usr/share/doc/vmcaster'
    cfg_files_installdir = "etc/vmcaster"


from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(name='vmcaster',
    version=version,
    description="""vmcaster is a simple tool for managing and updating your published virtual machines image lists. Following the Hepix image list format.""",
    long_description="""vmcaster was designed with the realisation that users typically create new virtual machines images rarely but update them frequently. Most other tools for marking up image lists don't minimise the amount of data entry for updates. vmcaster attempts to be the first of a new generation of image list publishers. the tasks of updating an image and uploading a fresh signed imagelist have been made as painless as possible as these are the most common tasks.""",
    author="O M Synge",
    author_email="owen.synge@desy.de",
    license='Apache License (2.0)',
    install_requires=[
       "sqlalchemy>=0.5",
       "M2Crypto>=0.16",
        ],
    url = 'https://svnsrv.desy.de/desy/grid-virt/org.desy.dish.updator',
    classifiers=[
        'Development Status :: 4 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research'
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    packages=['vmcasterpub', 'vmcasterpub.tests'],
    scripts=['vmcaster'],

    data_files=[(doc_files_installdir, ['README.md', 'ChangeLog', 'LICENSE']),
        (cfg_files_installdir, ['vmcaster.cfg.template']) ],
    tests_require=[
        'coverage >= 3.0',
        'pytest',
        'mock',
        'SQLAlchemy >= 0.7.8',
    ],
    setup_requires=[
        'SQLAlchemy >= 0.7.8',
    ],
    cmdclass = {'test': PyTest},
    )
