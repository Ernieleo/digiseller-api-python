from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='digiseller_api_python',
    version='1.4.2',
    author='Ernieleo',
    author_email='ernieleo@vk.com',
    description='Interaction with Digiseller API via Python',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ernieleo/Digiseller-API-Python',
    packages=find_packages(),
    install_requires=['requests>=2.31.0'],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='digiseller api python',
    project_urls={
        'Documentation': 'https://my.digiseller.com/inside/api.asp',
        'Download': 'https://pypi.org/project/digiseller-api-python/',
        'Write me': 'https://t.me/ernieleo'
    },
    python_requires='>=3.8'
)
