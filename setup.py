from setuptools import setup, find_packages

setup(name='django-key',
      version='0.5.0',
      description='Simple, straight forward API key for django-piston.',
      author='Steve Coursen',
      author_email='smcoursen@gmail.com',
      packages=find_packages(),
      license="BSD",
      url="https://github.com/scoursen/django-apikey",
      install_requires=['setuptools',],
      include_package_data=True,
      setup_requires=['setuptools_git',],
)
