from setuptools import setup, find_packages

setup(name="chess",
      packages=find_packages(),
      entry_points={
    'console_scripts': [
        'chess = chess.main:main',
    ],
},)
