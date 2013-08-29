from setuptools import setup, find_packages

setup(
    name="buzzfeed",
    install_requires=['pymarkovchain', 'tweepy'],
    version="0.1",
    packages=['buzzfeed', 'buzzfeed.static'],
    package_data = {
        'buzzfeed.static': ['*'],
    },
    entry_points={
        'console_scripts': [
            'buzzfeedr = buzzfeed:main'
        ]}
)

