try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
        'description': 'School PIC18F simulator',
        'author': 'Maksim Milyutin',
        'url': '',
        'download_url': 'https://github.com/maksm90/minipic',
        'author_email': 'milyutinma@gmail.com',
        'version': '0.1',
        'install_requires': ['nose'],
        'packages': ['minipic'],
        'scripts': [],
        'name': 'minipic'
}

setup(**config)
