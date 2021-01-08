import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup = {
    'url':'https://github.com/UCL-EO/geog0133-Practicals',
    'version':'1.0.1',
    'name':'geog0133-Practicals',
    'description':'UCL Geography MSc notes',
    'author':'Prof. P. Lewis',
    'author_email':'p.lewis@ucl.ac.uk',
    'license':'MIT',
    'keywords':'Terrestrial Carbon: modelling and monitoring',
    'long_description':long_description,
    'long_description_content_type':"text/markdown",
    'packages':setuptools.find_packages(),
    'classifiers':[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    'python_requires':'>=3.6',
}


setuptools.setup(**setup) 

