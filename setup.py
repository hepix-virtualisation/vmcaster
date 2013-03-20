from sys import version_info
from vmcasterpub.__version__ import version
if version_info < (2, 6):
	from distutils.core import setup
else:
	try:
        	from setuptools import setup, find_packages
	except ImportError:
        	from ez_setup import use_setuptools
        	use_setuptools()
        	from setuptools import setup, find_packages


setup(name='vmcaster',
    version=version,
    description="""vmcaster is a simple tool for managing and updating your published virtual machines image lists. Following the Hepix image list format.""",
    long_description="""vmcaster was designed with the realisation that users typically create new virtual machines images rarely but update them frequently. Most other tools for marking up image lists don't minimise the amount of data entry for updates. vmcaster attempts to be the first of a new generation of image list publishers. the tasks of updating an image and uploading a fresh signed imagelist have been made as painless as possible as these are the most common tasks.""",
    author="O M Synge",
    author_email="owen.synge@desy.de",
    license='Apache License (2.0)',
    install_requires=[
       "sqlalchemy>=0.5",
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
    packages=['vmcasterpub'],
    scripts=['vmcaster'],
    data_files=[('/usr/share/doc/vmcaster',['README.md']),
        ('/etc/vmcaster',['vmcaster.cfg.template'])],
    )
