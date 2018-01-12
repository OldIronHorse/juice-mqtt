#!/usr/bin/env python3
from setuptools import setup

setup(name='juice-mqtt',
      version='0.1',
      description='An MQTT <-> Squeezebox CLI bridge',
      author='OldIronHorse',
      author_email='',
      license='GPL 3.0',
      packages=['juice_mqtt'],
      install_requires=['juice','paho-mqtt'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
