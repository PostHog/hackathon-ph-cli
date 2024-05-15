from setuptools import setup, find_packages

setup(
    name='ph',
    version='1.0.0',
    packages=find_packages(),
    package_data={},    
    install_requires=[
        'click==8.1.7',
        'rich==13.7.0',
        'requests==2.31.0',
        'inquirer==3.2.4'
    ],
    entry_points={
        'console_scripts': [
            'ph=ph.main:main',
        ],
    },
    author='Posthog',
    author_email='daniel@posthog.com, manoel@posthog.com',
    description='Posthog CLI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Posthog/hackathon-ph-cli',
)
