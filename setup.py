from distutils.core import setup

setup(name='bliknetlib',
      version='1.0.5',
      description='Python IoT integration utilities',
      long_description='Python IoT integration utilities',
      author='Geurt Lagemaat',
      author_email='geurtlagemaat@gmail.com',
      packages=['bliknetlib'],
      package_dir={'bliknetlib': 'src/bliknetlib'},
      package_data={'bliknetlib': ['data/*.dat']}
      )