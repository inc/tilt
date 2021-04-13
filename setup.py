from setuptools import setup, find_packages
import pathlib

setup(
    name='tilt',
    version='0.0.1',
    description='Tilt',
    url='https://tilt.cash',
    author_email='info@tilt.cash',
    license='Lone Dynamics Open License',
    packages=['tilt', 'tilt.wlt'],
    python_requires='>=3.6, <4',
    install_requires=[
        'cryptography',
        'bitcoinlib',
        'websocket-client',
        'requests',
        'pyzmq'
    ],
    entry_points={
        'console_scripts': [
            'tilt=tilt.cli:main'
        ]
    },
    project_urls={
        'Bug Reports': 'https://github.com/inc/tilt/issues',
        'Source': 'https://github.com/inc/tilt'
    }
)
