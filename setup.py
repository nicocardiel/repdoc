from setuptools import setup
from setuptools import find_packages

def setup_package():

    from repdoc import __version__
    REQUIRES = ['numpy', 'pandas', 'argparse', 'PySimpleGUI']
    META_DATA = dict(
        name='repdoc',
        version=__version__,
        description='subject assignment tool',
        author='Nicolas Cardiel',
        author_email='cardiel@ucm.es',
        packages=find_packages('.'),
        entry_points={
            'console_scripts': [
                'repdoc = repdoc:main'
            ],
            },
        setup_requires=['repdoc'],
        install_requires=REQUIRES,
        zip_safe=False
        )

    setup(**META_DATA)


if __name__ == '__main__':
    setup_package()
