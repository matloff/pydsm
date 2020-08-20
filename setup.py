import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="py-dsm",
	version="1.1.1",
	author="Daniel Guo, Norm Matloff",
	author_email="zhyguo@ucdavis.edu, matloff@cs.ucdavis.edu",
	description="Python true-shared memory parallel computation",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/matloff/pydsm",
	py_modules=["pydsm"],
	classifiers= [
		"Intended Audience :: Developers",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: MIT License",
		"Topic :: Scientific/Engineering",
		"Operating System :: Unix",
		"Operating System :: POSIX",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8"
	],
	keywords="shared memory parallel concurrent multiprocessing numpy",
	install_requires=['SharedArray', 'numpy']
)
