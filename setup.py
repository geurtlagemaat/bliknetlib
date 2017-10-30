from distutils.core import setup

install_requires = [
    'twisted==16.4.1',
    'circus==0.14.0'
    'concurrentloghandler>=0.9.1'
    'paho-mqtt==1.3.1'
]

setup(name='bliknetlib',
      version='1.0.3',
      description='Python IoT integration utilities',
      long_description='Python IoT integration utilities',
      author='Geurt Lagemaat',
      author_email='geurtlagemaat@gmail.com',
      py_modules=['nodeControl', 'CircusNotifier', 'serialMsg', 'serialMsgQueues'],
      )