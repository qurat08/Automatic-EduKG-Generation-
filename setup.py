from setuptools import setup, find_packages

with open("./requirements.txt") as reqs_text:
    requirements = [line for line in reqs_text]

with open("./test-requirements.txt") as test_reqs_text:
    test_requirements = [line for line in test_reqs_text]

with open("./docs-requirements.txt") as docs_reqs_text:
    docs_requirements = [line for line in docs_reqs_text]

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setup(name="cmkg",
      packages=find_packages(exclude=['docs', 'tests']),
      version="0.1.0",
      author="",
      author_email="",
      description="",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="",
      keywords="nlp flair transformers keyword extraction embeddings",
      classifiers=[
          "Programming Language :: Python",
          "Intended Audience :: Science/Research",
          "Intended Audience :: Developers",
          "Topic :: Scientific/Engineering :: Natural Language Processing",
          "Licence :: MIT Licence",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Operating System :: Unix",
          "Operating System :: MacOS",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.8",
      ],
      dependency_links=[],
      install_requires=requirements,
      extras_require={
          "docs": docs_requirements,
          "test": test_requirements
      },
      python_requires='>=3.6',
      zip_safe=False)
