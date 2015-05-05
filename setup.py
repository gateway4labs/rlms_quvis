#-*-*- encoding: utf-8 -*-*-
from setuptools import setup

classifiers=[
    "Development Status :: 3 - Alpha",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: Freely Distributable",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]

cp_license="MIT"

setup(name='g4l_rlms_quvis',
      version='0.1',
      description="QuVis: The University of St Andrews Quantum Mechanics Visualisation project plug-in in the gateway4labs project",
      classifiers=classifiers,
      author='Pablo Orduña',
      author_email='pablo.orduna@deusto.es',
      url='http://github.com/gateway4labs/rlms_quvis/',
      license=cp_license,
      py_modules=['g4l_rlms_quvis'],
     )
