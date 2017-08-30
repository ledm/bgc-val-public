from setuptools import setup

MAJOR               = 0
MINOR               = 1
VERSION = '{}.{}'.format(MAJOR, MINOR)

######
# Use pip to install this script:
# pip install -e . --user

setup(name="bgc-val",
      version=VERSION,
      description="BGC-val is a suite to evaluating the scientific performance of a 3D marine model.",
      author="Lee de Mora (PML)",
      author_email="ledm@pml.ac.uk",
      url="https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/bgc-val-public",
      license='Revised Berkeley Software Distribution (BSD) 3-clause license.',
      classifiers=[
          'Development Status :: 1 - Alpha',
          'Intended Audience :: Scientific researcher',
          'Topic :: Model evaluation',
          'License :: OSI Approved :: BSD3 License',
          'Programming Language :: Python :: 2.7',
          'Operating System :: UNIX',
      ],
      install_requires=[
          "numpy",
          "netCDF4", 
          "scipy",
          "datetime",
          "cartopy",
          "netcdf_manip",
      ],
      )


