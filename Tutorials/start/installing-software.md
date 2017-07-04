# Installing Faraday Software
The open source software provided by FaradayRF is primarily written in Python. Any language capable of interfacing with a serial port or TCP/IP socket could be used. However, we chose Python 2.7 due to its ease of learning and cross-platform capabilities.

> Please note that no testing has been performed with Python 3 at this time. If you do, please consider helping us update!

## Installing Python 2.7
### Windows
The Hitchhiker's Guide To Python: [Installing Python on Windows](http://docs.python-guide.org/en/latest/starting/install/win/)

### Linux (Debian-based)
Most distributions come with Python preinstalled, however if not please read the [Python Documentation](https://docs.python.org/2/using/unix.html#getting-and-installing-the-latest-version-of-python)

### Max OS X
Most OS X versions already contain a [version of Python](https://wiki.python.org/moin/BeginnersGuide/Download).

#### Installing Pip
If you are using Debian 8 you will need to install pip. Otherwise you already have it with Python.
* ```sudo apt-get install python-pip```

#### Mac OS X
* Follow The Hitchhiker's Guide to [Installing Python on Max OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)
  * XCode
  * Homebrew
  * Python 2.7
  * Setuptools
  * Pip
  * Optional: Virtual Environments

> A basic version of Git comes on OS X. Apple Git-50.3 was used to write this guide but consider upgrading it or installing the official Git for OS X.

# Obtaining Faraday Software
Faraday software is available on the [Python Package Index](https://pypi.python.org/pypi/faraday/) and can be installed from PyPI with `pip`. This makes installation a breeze if you do not want to contribute code back into our Github repository.

If you do want to help the project by contributing code back into our repository then please follow the *Installing in Pip Editable Mode* section.

## Installing from PyPI
Just want to run the latest `faraday` software? Open up a command prompt and execute the following commands:

* `pip install faraday`

That's it!

## Installing in Pip Editable Mode
If you want to be able to develop with faraday software then we suggest cloning our Git Repository as described below and install with pip in 'editable' mode. Please note that in 'editable' mode you may have to run faraday software from the root project directory due to filepath issues when running in this mode.

Checkout the Git repository as explained below and then install with the following:
* Navigate to the repository root directory
* `pip install -e .`

### Windows

The open-source software is provided on our GitHub repository. This guide assumes [Git is installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) along with Git Bash.

Using Git Bash (right-click|Git Bash here) this example will be relative to wherever you start bash:

1. Create a suitable folder for Faraday software. i.e. `mkdir -p git/faradayrf`
2. Navigate to the new folder `cd git/faradayrf`
3. Clone the lastest master branch `git clone https://github.com/FaradayRF/Faraday-Software.git software`
4. Navigate to the software `cd software`
5. Install in pip editable mode with `pip install -e .`

Now you can use faraday the same as performing a `pip install faraday` however almost all changes to the code in your git clone will automatically be available from command line. Please note that changes to `setuptools` configuration in `setup.cfg` such as adding a new application command line option will require reinstalling in editable mode.

> Consider [forking our repository](https://help.github.com/articles/fork-a-repo/) instead!

### Linux (Debian-Based)
This guide assumes [Git is installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

1. Create suitable folder for Faraday software. I.e. ```mkdir -pit/faradayrf```
2. Navigate to the new folder ```cd git/faradayrf```
3. Clone latest master branch ```git clone https://github.com/FaradayRF/Faraday-Software.git software```
4. Navigate to the software `cd software`
5. Install in pip editable mode with `pip install -e .`

Now you can use faraday the same as performing a `pip install faraday` however almost all changes to the code in your git clone will automatically be available from command line. Please note that changes to `setuptools` configuration in `setup.cfg` such as adding a new application command line option will require reinstalling in editable mode.

> Consider [forking our repository](https://help.github.com/articles/fork-a-repo/) instead!

### Mac OS X
This guide assumes [Git is installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). A basic and suitable Git is installed on all OS X computers but it is a stripped-down version.

1. Create suitable folder for Faraday software. I.e. ```mkdir -p git/faradayrf```
2. Navigate to the new folder ```cd git/faradayrf```
3. Clone latest master branch ```git clone https://github.com/FaradayRF/Faraday-Software.git software```
4. Navigate to the software `cd software`
5. Install in pip editable mode with `pip install -e .`

Now you can use faraday the same as performing a `pip install faraday` however almost all changes to the code in your git clone will automatically be available from command line. Please note that changes to `setuptools` configuration in `setup.cfg` such as adding a new application command line option will require reinstalling in editable mode.

> Consider [forking our repository](https://help.github.com/articles/fork-a-repo/) instead!

# Plugging Faraday in
Congratulations! Making it this far means that you're so close to using Faraday. However we need to [plug in the Faraday hardware](connecting-hardware.md) and complete configuration before running the software.
