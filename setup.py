from setuptools import setup

setup_args = dict(
    name='nosedep',
    version='0.1',
    url='https://bitbucket.org/Zitrax/nose-dep',
    maintainer='Daniel Bengtsson',
    maintainer_email='daniel@bengtssons.info',
    description='Nose test dependency support',
    long_description=open('README.md').read(),
    license='MIT',
    py_modules=['nosedep'],
    zip_safe=False,
    entry_points={
        'nose.plugins.0.10': [
            'nosedep = nosedep:NoseDep'
            ]
        }
    )

if __name__ == '__main__':
    setup(install_requires=['nose', 'toposort'],
          **setup_args)
