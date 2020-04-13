from setuptools import setup
from setuptools import find_packages

setup(
  name='rsyslog_cee',
  version='0.1.0',
  description='python support for an rsyslog cee logger',
  url='https://github.com/victusfate/rsyslog_cee',
  author='victusfate',
  author_email='messel@gmail.com',
  license='MIT',
  packages=find_packages(),
  install_requires = [
  ],
  zip_safe=False
)
