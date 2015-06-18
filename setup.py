from setuptools import setup

setup_args = dict(
    name='nosedep',
    version='0.1',
    #url='http://github.com/',
    maintainer='Daniel Bengtsson',
    maintainer_email='daniel@bengtssons.info',
    description='Nose test dependency support',
    #long_description=open('README').read(),
    install_requires=['nose'],
    license='GNU GPLv3+',
    py_modules=['nosedep'],
    zip_safe=False,
    entry_points={
        'nose.plugins.0.10': [
            'nosedep = nosedep:NoseDep'
            ]
        }
    )

if __name__ == '__main__':
    setup(**setup_args)
