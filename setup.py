#!/usr/bin/env python
#==========================================================================#
#  This Python file is part of myfempy project                             #
#                                                                          #
#  The code is written by A. V. G. Campos                                  #
#                                                                          #
#  A github repository, with the most up to date version of the code,      #
#  can be found here:                                                      #
#     https://github.com/easycae-3d/myfempy                                #
#                                                                          #
#  The code is open source and intended for educational and scientific     #
#  purposes only. If you use myfempy in your research, the developers      #
#  would be grateful if you could cite this.                               #  
#                                                                          #
#  Disclaimer:                                                             #
#  The authors reserve all rights but do not guarantee that the code is    #
#  free from errors. Furthermore, the authors shall not be liable in any   #
#  event caused by the use of the program.                                 #
#==========================================================================#
"""
#==========================================================================#
                                __                                
             _ __ ___   _   _  / _|  ___  _ __ ___   _ __   _   _ 
            | '_ ` _ \ | | | || |_  / _ \| '_ ` _ \ | '_ \ | | | |
            | | | | | || |_| ||  _||  __/| | | | | || |_) || |_| |
            |_| |_| |_| \__, ||_|   \___||_| |_| |_|| .__/  \__, |
                        |___/                       |_|     |___/ 

~~~         myfempy -- MultiphYsics Finite Element Method with PYthon    ~~~
~~~                     COMPUTATIONAL ANALYSIS PROGRAM                   ~~~
~~~                    PROGRAMA DE ANÁLISE COMPUTACIONAL                 ~~~
~~~             Copyright (C) 2022 Antonio Vinicius Garcia Campos        ~~~
#==========================================================================#
myfempy install script

Install myfempy through `python setup.py install`,
or visit the github page to more information
"""
# SETUP SYSTEM
from setuptools import setup, find_packages

# README 
with open('README.md', 'r', encoding="utf-8") as ld:
    long_description = ld.read()

# VERSION
from myfempy import version

# --------------
setup(
    python_requires=">=3",
    include_package_data=True,
    name="myfempy",
    version=version.__version__,
    license="GNU",
    license_files=["LICENSE.txt"],
    author="Campos, A. V. G.",
    maintainer="Campos, A. V. G. & 3D EasyCAE",
    maintainer_email="3deasycaebr.contato@gmail.com",
    description="myfempy is a python package to scientific analysis based on finite element method",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://myfempy.readthedocs.io/en/latest/",
    download_url="https://github.com/easycae-3d/myfempy",
    keywords=["Finite Element", "Mechanics", "Python Package"],
    packages=find_packages(),
    package_dir={
        "myfempy": "myfempy",
    },
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "matplotlib>=3.6",
        "cython>=0.29",
        "art>=5.8",
        "colorama>=0.4",
        "vedo>=2023.4",
    ],
    # include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 1 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Physics",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOSX",
    ],
)
