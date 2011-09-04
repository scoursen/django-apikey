from setuptools import setup, find_packages

setup(name='django-apikey',
      version='0.5.0'
      description='Simple, straight forward API key for django-piston.',
      author='Steve Coursen',
      author_email='me@stevecoursen.com',
      packages=find_packages(),
      install_requires=['setuptools',],
      include_package_data=True,
      setup_requires=['setuptools_git',],
)
