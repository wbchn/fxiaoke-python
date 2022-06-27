from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fxiaoke-python',
    version="0.0.1",
    description='fxiaoke CRM(ShareCRM) api.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    packages=['fxiaoke'],
    install_requires=['requests>=2.26.0'],
    author='wbin',
    author_email='wbin.chn@gmail.com',
    url='https://github.com/wbchn/fxiaoke-python',
    python_requires='~=3.8',
)