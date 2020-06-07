from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.readlines()

long_description = (
    "Deploy django application to virtual private server just by running one single command."
    "Deploy it automatically generates configuration files for Nginx and Gunicorn so you don't"
    " have to worry about it. :)"
)

setup(
    name="deploy_it",
    version="0.3.3",
    author="Apoorva Singh",
    author_email="apoorva.singh157@gmail.com",
    url="https://github.com/meticulousCraftman/deploy_it",
    description="Deploy Django projects to virtual private server in a single command.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    entry_points={"console_scripts": ["deploy_it = deploy_it.main:main"]},
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    keywords="python devops django gunicorn nginx",
    install_requires=requirements,
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
)
