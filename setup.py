from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='digiseller_api_python',
    version='1.4.1',
    author='Ernieleo',
    author_email='ernieleo@vk.com',
    description='Interaction with Digiseller API',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ernieleo/Digiseller-API-Python',
    packages=find_packages(),
    install_requires=['requests>=2.31.0'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='api client',
    project_urls={
        'Documentation': 'https://my.digiseller.com/inside/api.asp'
    },
    python_requires='>=3.7'
)
