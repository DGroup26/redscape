from setuptools import setup, find_packages  
  
setup(  
    name="redscape",  
    version="1.0.0",  
    packages=find_packages(),  
    install_requires=[  
        'click>=8.0',  
        'playwright>=1.40',  
        'beautifulsoup4>=4.12',  
        'requests>=2.31',  
        'rich>=13.0',  
        'pyyaml>=6.0',  
        'flask>=2.3',  
        'weasyprint>=60.0',  
        'pillow>=10.0',  
    ],  
    entry_points={  
        'console_scripts': [  
            'redscape=redscape.cli:cli',  
        ],  
    },  
    python_requires='>=3.9',  
    author="redreplica",  
    description="Redscape",  
    url="https://github.com/DGroup26/redscape",  
)  