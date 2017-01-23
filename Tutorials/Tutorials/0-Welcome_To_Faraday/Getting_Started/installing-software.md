# Installing Faraday Software
The open source Faraday software provided by FaradayRF is primarily written in Python. Any language capable of interfacing with a serial port could be used however we chose Python 2.7 due to it's ease of learning and cross-platform capabilities.

Please note that no testing has been performed with Python 3 at this time. If you do, please let us know!

This guide is also a work in progress and has been written using a Windows environment. It will be updated as possible with other operating system specific steps.

## Installing Python 2.7
### Windows
 * The Hitchhiker's Guide To Python: [Installing Python on Windows](http://docs.python-guide.org/en/latest/starting/install/win/)
 
### Linux (Debian-based)
Most distributions come with Python preinstalled, however if not please read the [Python Documentation](https://docs.python.org/2/using/unix.html#getting-and-installing-the-latest-version-of-python)


### Mac OS X
Python 2.7 should come installed on OS X. however it does not include all necessary development packages and tools. You should install these if necessary:
 * The Hitchhiker's Guide To Python: [Installing Python on Mac OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)
 
##Faraday Software
### Git Repository
> Skip to "Zip File Installation" if you do not plan on forking/commiting new code to GitHub

The open-source software is provided on our GitHub repository. If you plan on developing software you should [install GIT](https://git-scm.com/) on your computer and checkout the GitHub repository. We assume you know how to do this if you are thinking about developing software.

Latest Master: https://github.com/FaradayRF/Faraday-Software.git

###Zip File Installation
This guide will simply download the latest stable software
 1. Faraday Software Zip: https://github.com/FaradayRF/Faraday-Software/archive/master.zip
 2. Unzip contents into desired location i.e. ```C:\faradayrf```
 3. Navigate to your unzipped file ```C:\faradayrf\Faraday-Software-master```

##Installing Required Python Packages

 ```C:\faradayrf\Faraday-Software-master> pip install -r requirements.txt```
 
# Plugging it Together
Congratulations! Making it this far means that the software is nearly ready. However we need to [plug in the Faraday hardware](connecting-hardware.md) to complete configuration.