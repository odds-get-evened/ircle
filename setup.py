from setuptools import setup, find_packages

setup(
    name="ircle",
    author="Chris Walsh",
    author_email="chris.is.rad@pm.me",
    classifiers=[],
    description="an IRC bot to trigger heartbeats for time sync integrity. `did i do that?!`",
    license="MIT",
    version="0.0.1",
    url="",
    packages=find_packages(),
    install_requires=[
        'chardet'
    ],
    entry_points={
        'console_scripts': [
            'ircle = boot:initialize'
        ]
    }
)