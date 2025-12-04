from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='digiseller-api-python',
    version='3.1.1',
    author='Ernieleo',
    author_email='ernieleo@offnik.ru',
    description='Python wrapper package for easy integration with the Digiseller API',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ernieleo/Digiseller-API-Python',
    packages=find_packages(),
    install_requires=['httpx>=0.26.0'],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='digiseller api python wrapper',
    project_urls={
        'API Documentation': 'https://my.digiseller.com/inside/api.asp',
        'Write me': 'https://t.me/ernieleo'
    },
    python_requires='>=3.8'
)
