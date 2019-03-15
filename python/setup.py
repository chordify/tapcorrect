from setuptools import setup, find_packages

setup(name='tapcorrect',
      version='0.1',
      packages=find_packages(),
      description='algorithms for automatically correcting tapped beat annotations',
      author='Jonathan Driedger',
      author_email='jonathan@chordify.net',
      license='Attribution 3.0 Unported (CC BY 3.0)',
      install_requires=[
          'madmom',
          'librosa',
          'matplotlib',
          'numpy',
          'csv',
          'pickle'
      ],
      include_package_data=True,
      zip_safe=False)