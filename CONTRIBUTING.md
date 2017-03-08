# Contributor Guidelines

Faraday-Software is the software that interfaces the Faraday radio designed and manufactured by [FaradayRF](https://faradayrf.com/). We're excited you are considering helping out. We need it! FaradayRF was formed to provide the necessary hardware and software to enable the shift towards a data-centric amateur radio.

> Data is the future of amateur radio and we believe it will be open

By contributing to this project you are helping an open source project. That means that while FaradayRF benefits from it, so does the amateur radio community as a whole. Everyone has access to the work, everyone can use it. We like that.

## Essential Reading

You may wonder why we have made some of the decisions with the direction and functionality of this project. Our [Master Plan](https://faradayrf.com/faradayrf-master-plan/) outlines our goals clearly.

 1. Educate the Masses
 2. Build New Infrastructure
 3. Expand Spectrum Use

This points to why we may argue that Faraday software or hardware isn't designed to be the competitive with high bandwidth WiFi or why we are not currently developing a Mesh network. These items add complexity that do not help us accomplish these three goals.

## Before Getting Started

### Overview
* [Code of Conduct](#code_of_conduct)
* [Core Principles](#core_principles)
* [Suggested Tools](#suggested_tools)

### How To Contribute

* [Reporting a Bug](#reporting_a_bug)
* [Feature Requests](#feature_requests)
* [Beginners Start Here](#beginners_start_here)
* [Pull Requests](#pull_requests)

### Style Guides

* [Git](#git)
* [Writing](#writing) 
* [Documentation](#documentation)
* [Python](#python)
* [Javascript](#javascript)
* [HTML](#html)
* [C](#c)

##Overview

## Code of Conduct<a name="code_of_conduct"></a>
FaradayRF in interested in developing better technology and educational resources for ham radio. It's that simple. This means FaradayRF and all contributors pledge to foster a welcoming atmosphere for everyone. Participating with this project shall be a harassment-free irrespective of nationality, age, body size, ethnicity, gender identity and expression, any disabilities, level of experience, personal appearance, race, religion, or sexual identity/orientation.

If you feel that you or someone participating in this project is being harassed please contact Support@FaradayRF.com.

## Core Principles <a name="core_principles"></a>
Faraday-Software is being developed for the [Faraday radio](https://faradayrf.com/faraday/). However, this open source project also strives to push ham radio forward. Not just for FaradayRF but for everyone. Therefore we ask that all contributors take the following principles to heart:

* Applications and supporting programs shall strive to be [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer)
* Functionality of the software shall attempt to be agnostic of radio hardware design where appropriate
* An [API](https://en.wikipedia.org/wiki/Application_programming_interface) should be used to communicate between different applications and progams

## Suggested Tools<a name="suggested_tools"></a>
Tools we find make developing for Faraday-Software better

* [Git](https://git-scm.com/) - If you want to contribute you will need Git
* [PyCharm](https://www.jetbrains.com/pycharm/?fromMenu) - Python IDE
* [PyScripter](https://sourceforge.net/projects/pyscripter/) - Python IDE
* [Notepad++](https://notepad-plus-plus.org/) - Free and powerful text editor
* [pep8](https://pypi.python.org/pypi/pep8) - PEP8 Python module

# How To Contribute <a name="how_to_contribute"></a>

---

## Bug Reporting <a name="bug_reporting"></a>

Following these simple guidelines will help the maintainers better understand your bug report and to ensure a quality solution. Not all guidelines may be applicable to a given situation, please provide as much as possible.

* **Perform basic debugging**
  * Are you using the latest version?
  * Have you changed your configuration of both software or Faraday device from default? (if so please specify)
  * Are multiple programs running that may be interfering?
* **Use a clear and descriptive title****
* **Describe the exact steps used to reproduce the bug**
* **Describe the exact problem behavior you observed**
* **Provide a demonstration if possible**
  * An application script, log file, screenshots, video, etc...
* **Explain what behavior you expected to see and why**
* **When in doubt provide as much information as possible**!

## Enhancement Suggestions <a name="enhancement_suggestions"></a>

Suggesting enhancements is one of the most important factors to driving innovation within the Faraday digital amateur radio community! Please follow as best as possible these guidelines to ensure that maintainers clearly understand the request.

* **Use a clear and descriptive title**
* **Provide a descriptive overview of the enhancements operation(s)**
  * In addition to text screenshots, diagrams, etc... are welcome if they better explain your suggestion
* **Explain why this is a useful enhancement to the community**


## Beginner Contributions <a name="beginner_contributions"></a>

If you are not sure how to start off contributing to the project browse the tagged beginner issues below.

* [Beginner Issues](https://github.com/FaradayRF/Faraday-Software/labels/Beginner) - Simple issues where the solution is likely a few lines of code or less
* [Documentation Updates](https://github.com/FaradayRF/Faraday-Software/labels/Documentation) - Clear and consistent documentation is key to building a knowledgeable and growing community


##Pull Requests <a name="pull_requests"></a>

* Include examples/screenshots/videos of your pull request if applicable
* Include a detailed description of the pull requests purpose
* Follow our code [style guidelines](#styleguides)
* Avoid platform dependent code
 

#Styleguides <a name="styleguides"></a>
---

## Python PEP8 <a name="pep8"></a>

All Faraday Python code is styled using [PEP8](https://www.python.org/dev/peps/pep-0008/), existing code that does not meet this style guide is being updated to comply. There are several automatic PEP8 syntax checking programs such as the [PyCharm PEP8 Syntax Module](https://blog.jetbrains.com/pycharm/2013/02/long-awaited-pep-8-checks-on-the-fly-improved-doctest-support-and-more-in-pycharm-2-7/).

## Documentation <a name="documentation"></a>

Documentation is mandatory to ensure that all contributors clearly understand how to use, enhance, and fix additions to the project. Faraday uses [Sphinx](http://www.sphinx-doc.org/en/stable/index.html) to provide dynamic documentation and is hosted on [Faraday's Read The Doc's Page](http://faraday-software.readthedocs.io/en/latest/).

* [Sphinx Documentation](http://www.sphinx-doc.org/en/stable/contents.html)
* [Examples Of Good Python Docstrings](http://www.sphinx-doc.org/en/stable/ext/example_google.html)

##Configuration files

For any application that requires user specific configuration, add a sample configuration file with `.sample` added to the file name before the `.ini`. Use proxy as an example where `proxy.py` uses configuration from `proxy.ini`, but `proxy.sample.ini` is stored in git and `proxy.ini` is in .gitignore. The end user needs to create their own local copy of the configuration file that contains their information by editing the file and renaming it without the `.sample`.

Use the following format within configuration files:
* Uppercase [SECTION] and NAME fields but values can be upper or lowercase
`[SECTION]`
* No spaces before or after = separating the NAME from the value
`NAME=value`
* Comments must be on their own line and cannot be inline comments
`;this is a comment`