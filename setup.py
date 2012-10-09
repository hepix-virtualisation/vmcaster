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


setup(name='dish-updator',
    version=version,
    description="Updates image lists.",
    long_description="""A tool for updating image lists using a local db to store state.""",
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
    data_files=[('/usr/share/doc/vmcaster',['README']),
        ('/etc/vmcaster',['vmcaster.cfg.template'])],
    )
