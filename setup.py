__author__ = 'John Wood'
# Created on 01/29/21

from setuptools import setup


with open('README.md', 'r') as f:
	ld = f.read()
with open('requirements.txt') as f:
	req = f.read().splitlines()

setup(
	name='xnat_wrapper',
	author='John W Wood',
	author_email='jwwood@mdanderson.org',
	version='0.1.0',
	description='Tools for reading dicom files, RT structures, and dose files, as well as tools for '
				'converting numpy prediction masks back to an RT structure',
	long_description=ld,
	long_description_content_type="text/markdown",
	url='https://github.com/jwood1290/XNAT_Wrapper',
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
	],
	install_requires=req
)