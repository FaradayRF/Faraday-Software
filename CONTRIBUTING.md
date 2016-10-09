# Contributor Guidelines

First, we would like to thank you for contributing to the open source project!

This document contains information relavent to anyone wishing to contribute the [Faraday digital radio](https://faradayrf.com) host computer software. Our core mission is laid out in our [Master Plan](https://faradayrf.com/faradayrf-master-plan/) and all contributions to the main project should help enable these goal set out.

[What should I know before I get started](#get_started)

* [Code of Coduct](#code_of_conduct)
* [Software Design and Purpose](#software_design)
* [Language(s)](#language)
* [Tools](#tools)

[How To Contribute](#how_to_contribute)

* [Bug Reports](#bug_reporting)
* [Suggesting Enhancements](#enhancement_suggestions)
* [Beginner Contributions](#beginner_contributions)
* [Pull Requests](#pull_requests)

[Styleguides](#styleguides)

* [Documentaion](#documentation)
* [Python - PEP8](#pep8)

#What Should I Know Before I Get Started <a name="get_started"></a>
---

##Software Design and Purpose <a name="software_design"></a>
The Faraday software is responsible for providing host computer functionality when a locally connected Faraday digital radio is connected. As described on the [Code Overview](https://faradayrf.com/code/) page, this software provides:

* RESTful API interface to interact with a local Faraday
* Application toolset to utilize the RESTful API in a Python script
* Core applications


## Language <a name="language"></a>
Faraday Software is written in [Python 2.7](https://www.python.org/downloads/).

###Notable Python Modules <a name="notable_python_modules"></a>
Notable additional Python modules in use are:

* [FLASK](http://flask.pocoo.org/) - A microframework for web development that is used to transfer information between Faraday and applications over a network interface (primarally localhost)

## Tools<a name="tools"></a>
Please use the tools of your choice but we recommend:

* [PyCharm](https://www.jetbrains.com/pycharm/?fromMenu) - Feature rich Python IDE with built it tools such as a PEP8 syntax checker.
* [PyScripter](https://sourceforge.net/projects/pyscripter/) - A lightweight Python IDE (for Windows)

# How To Contribute <a name="how_to_contribute"></a>

---

## Bug Reporting <a name="bug_reporting"></a>

Following these simple guidelines will help the maintainers better understand your bug report and to ensure a quality solution. Not all guidelines may be applicable to a given situation, please provide as much as possible.

* **Perform basic debugging**
  * Are you using the latest version?
  * Have you changed your configuration of both software or Faraday device from default? (if so please specify)
  * Are multiple programs running that may be interferring?
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


## Begginer Contributions <a name="beginner_contributions"></a>

If you are not sure how to start off contributing to the project browse the tagged begginner issues below.

* Begginner Issues - Simple issues where the solution is likley a few lines of code or less
* Documentation Updates - Clear and consitant documenation is key to building a knowlegable and growing community

**TODO:** Add links to Github issue filters for the above.


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

Documentation is mandatory to ensure that all contributors clearly understand how to use, enhance, and fix additions to the project. Faraday uses [Sphinx}(http://www.sphinx-doc.org/en/stable/index.html) to provide dynamic documenation and is hosted on [Faraday's Read The Doc's Page](http://faraday-software.readthedocs.io/en/latest/).

* [Sphinx Documentation](http://www.sphinx-doc.org/en/stable/contents.html)
* [Examples Of Good Python Docstrings](http://www.sphinx-doc.org/en/stable/ext/example_google.html)