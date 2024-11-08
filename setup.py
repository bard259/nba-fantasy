from setuptools import setup, find_packages

setup(
    name="draft-supporter",                  # Package name
    version="0.1.0",                                 # Initial version
    description="A fantasy draft supporter tool",    # Short description
    author="Peijun Xu",
    author_email="ivanxu259@gmail.com",
    url="https://github.com/bard259/fantasy-draft-supporter",  # GitHub URL
    packages=find_packages(),                        # Automatically find package folders
    install_requires=[
        "numpy", "pandas", "pulp"                    # Add dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
