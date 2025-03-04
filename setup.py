from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='ev_range',
    version='0.1.0',
    description='EV Range Visualization Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='EV Range Team',
    author_email='example@example.com',
    url='https://github.com/yourusername/ev_range',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'ev-range=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
) 