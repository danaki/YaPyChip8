from setuptools import setup, find_packages

setup (
	name = 'YaPyChip8',
	version = '0.1',

	packages = find_packages(),

	scripts = ['main.py'],

	install_requires = ['pygame']
)
