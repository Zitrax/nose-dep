from setuptools import setup

setup_args = dict(
    name='nosedep',
    version='0.2',
    url='https://github.com/Zitrax/nose-dep',
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
    with open('requirements.txt') as f:
        required = f.read().splitlines()

    setup(install_requires=required,
          **setup_args)
