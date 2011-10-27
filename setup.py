from distutils.core import setup

setup(
    name='Builder',
    version='0.1.0',
    author='Brandon Ashworth',
    author_email='brandon@brandonashworth.com',
    packages=['builder', 'builder.api'],
    scripts=['bin/builder'],
    url='',
    license='LICENSE.txt',
    description='Simple tool/framework for automating tasks.',
    long_description='',
    install_requires=[
        "pyyaml",
        "jinja2",
    ],
)