from setuptools import find_packages, setup
from typing import List

def get_requirements(file_path:str)->List[str]:
    '''
    This function will return the list of requirements mentioned in the requirements.txt file
    '''
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace('\n', '') for req in requirements]

setup(
    name = 'Data-Science-Project',
    version = '0.0.1',
    author='Raiyan Sayeed',
    author_email = 'raiyansayeed0@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)
    

