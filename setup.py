import setuptools
from fastcapture import VERSION_STR

setuptools.setup(
    name='fastcapture',
    version=VERSION_STR,
    description='a (maybe dirty) implementation of webcam capture based on OpenCV on Python',
    url='https://github.com/gwappa/python-fastcapture',
    author='Keisuke Sehara',
    author_email='keisuke.sehara@gmail.com',
    license='MIT',
    install_requires=['numpy>=1.0','imutils>=0.5'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],
    packages=['fastcapture',],
    entry_points={
        'console_scripts': [
            'fastcapture=fastcapture.__init__:main'
        ]
    }
)
