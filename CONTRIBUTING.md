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
* [Configuration Files](#configuration_files)
* [Python](#python)
* [JavaScript](#javascript)
* [HTML](#html)
* [C](#c)

##Overview

### Code of Conduct<a name="code_of_conduct"></a>
FaradayRF in interested in developing better technology and educational resources for ham radio. It's that simple. This means FaradayRF and all contributors pledge to foster a welcoming atmosphere for everyone. Participating with this project shall be a harassment-free irrespective of nationality, age, body size, ethnicity, gender identity and expression, any disabilities, level of experience, personal appearance, race, religion, or sexual identity/orientation.

If you feel that you or someone participating in this project is being harassed please contact Support@FaradayRF.com.

### Core Principles <a name="core_principles"></a>
Faraday-Software is being developed for the [Faraday radio](https://faradayrf.com/faraday/). However, this open source project also strives to push ham radio forward. Not just for FaradayRF but for everyone. Therefore we ask that all contributors take the following principles to heart:

* Applications and supporting programs shall strive to be [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer)
* Functionality of the software shall attempt to be agnostic of radio hardware design where appropriate
* An [API](https://en.wikipedia.org/wiki/Application_programming_interface) should be used to communicate between different applications and progams

### Suggested Tools<a name="suggested_tools"></a>
Tools we find make developing for Faraday-Software better

* [Git](https://git-scm.com/) - If you want to contribute you will need Git
* [PyCharm](https://www.jetbrains.com/pycharm/?fromMenu) - Python IDE
* [PyScripter](https://sourceforge.net/projects/pyscripter/) - Python IDE
* [Notepad++](https://notepad-plus-plus.org/) - Free and powerful text editor
* [pep8](https://pypi.python.org/pypi/pep8) - PEP8 Python module
* [LICap](http://www.cockos.com/licecap/) - Easy to use GIF window capture

## How To Contribute

### Reporting a Bug <a name="reporting_a_bug"></a>

Following these simple guidelines will help the maintainers better understand your bug report. Not all guidelines may be applicable to a given situation, please use your best judgement.

* Perform basic debugging
* Are you using the latest version of the software?
* Have you changed your configuration of both software or Faraday device from default? (if so please provide your configuration files on a [Gist](https://gist.github.com/))
* Are multiple programs running that may be interfering?
* Use a clear and descriptive title
* Describe the exact steps used to reproduce the bug
* Describe the exact problem behavior you observed
* Provide a demonstration if possible (Youtube, [LICap](http://www.cockos.com/licecap/) GIF uploaded to ticket, etc)
* Explain what behavior you expected to see and why
* When in doubt provide as much information as possible!

### Feature Requests <a name="feature_requests"></a>

We love new ideas. If you think we should add functionality to the Faraday Software we want to hear about it. Please follow these guidelines as best as possible to help us understand your request. We cannot guarantee the feature will be implemented. In most cases the best way to get a feature into Faraday is to write the code and submit a Pull Request!

* Use a clear and descriptive title
* Provide a descriptive overview of the enhancements operation(s)
* Provide a demonstration if possible (Youtube, [LICap](http://www.cockos.com/licecap/) GIF uploaded to ticket, etc)
* Explain why this is a useful enhancement to the community

### Beginners Start Here <a name="beginners_start_here"></a>
FaradayRF welcomes all help. Even if you've never made an open source contribution before or don't even know how to program. We've marked bugs and enhancements that you may be able to contribute to the project with.

* [Beginner Issues](https://github.com/FaradayRF/Faraday-Software/labels/Beginner) - Simple issues where the solution is likely a few lines of code or less
* [Help Wanted](https://github.com/FaradayRF/Faraday-Software/labels/help%20wanted) - More involved tasks that require some knowlege of programming and can help learn how Faraday software ticks
* [Documentation Updates](https://github.com/FaradayRF/Faraday-Software/labels/Documentation) - Clear and consistent documentation is key to building a knowledgeable and growing community

### Pull Requests <a name="pull_requests"></a>

* Include a detailed description of the pull requests purpose
* Provide a demonstration if possible (Youtube, [LICap](http://www.cockos.com/licecap/) GIF uploaded to ticket, etc)
* Follow our code Style Guide wherever possible
* Avoid platform dependent code
 
## Style Guides

### Git<a name="git"></a>

#### Branches
* Choose short and descriptive branch names. i.e. `issue100`, `aprslib`
* Reference issue tickets in commits where applicable
* Delete your branch after it is merged unless there is reason not to

#### Commits
* Commits should be [atomic](https://seesparkbox.com/foundry/atomic_commits_with_git) i.e. one commit per logical change. Do not combine logical changes with formatting changes.
* Every commit should have a message associated with it describing the changes made
* Commit messages should reference issue ticket s i.e. "issue #90" and/or commits where appropriate

#### Merges
* Rebase branch to the branch it will be merged with to keep history simple and allow a fast-forward.
* Test code prior to merging

### Writing<a name="writing"></a>
There are many instances where one might find themselves writing for Faraday-Software. Mostly this will be documentation or comments. This project aims to be as clear as possible. Therefore we suggest abiding by the following conventions or you might find yourself being asked to fix your pull request.

* Spelling errors should be eliminated
* Try to be as clear and concise as possible
* Use one space after a period for new sentences
* When referencing variables, functions, classes, or folders use `code` formatting

### Documentation<a name="documentation"></a>
Open source projects strive then they are documented well. This allows everyone to understand what is going on in the code and how to use it. Please follow the following conventions:

* Use comments in sourcecode to explain a piece of code when the code does not speak for itself
* When writing functions and classes always use [Docstrings](https://www.python.org/dev/peps/pep-0257/)
* Every program, application, or library should have an associated `readme.md` describing what the code is, how to install it, and how to use it.
* If images are necessary, create an `images` folder within the project/application folder to hold them.

### Configuration files<a name="configuration_files"></a>

For any application that requires user specific configuration, add a sample configuration file with `.sample` added to the file name before the `.ini`. Use proxy as an example where `proxy.py` uses configuration from `proxy.ini`, but `proxy.sample.ini` is stored in git and `proxy.ini` is in .gitignore. The end user needs to create their own local copy of the configuration file that contains their information by editing the file and renaming it without the `.sample`.

Use the following format within configuration files:
* Uppercase [SECTION] and NAME fields but values can be upper or lowercase
`[SECTION]`
* No spaces before or after = separating the NAME from the value
`NAME=value`
* Comments must be on their own line and cannot be inline comments
`;this is a comment`

### Python<a name="python"></a>
Most code on Faraday-Software is Python. We are adhering to the [PEP8 style](https://www.python.org/dev/peps/pep-0257/) wherever possible. In most cases it is easy to abide but when cases arise that would be clearer to break PEP8 compliance we will consider this. Much of early Faraday-Software was written before PEP8 compliance was sought after and is therefore being updated over time. Please avoid combinging PEP8 updates to old code with new commits unles you are updating the code that is being changes to PEP8. Separate formatting and logical commits per out Git style guide!

* [PEP8 Python Module](https://pypi.python.org/pypi/pep8) - Run on sourcecode from command line to print out PEP8 violations
* [Pycharm PEP8 Support](https://blog.jetbrains.com/pycharm/2013/02/long-awaited-pep-8-checks-on-the-fly-improved-doctest-support-and-more-in-pycharm-2-7/) - Pycharm IDE has built-in PEP8 checking. Use it!

#### Naming Conventions
Faraday-Software started out with various naming schemes from its original developers. We are standardizing on PEP8 compliant naming schemes.

* **Function** names should be lowercase, with words seperated by underscores as necessary to improve readability
* **Variables** should also be lowercase and only deviating to improve readability
* **Class Names** should use CapWords convention
* **Package and module names** should use all lowercase names unless necessary then use underscores
* **Constants** should be all UPPERCASE

### JavaScript<a name="javascript"></a>
Javascript is often used for display functionality such as GUI interfaces or RESTful responses that return an HTML file. Please make an attempt to follow the [jQuery JavaScript Style Guide](https://contribute.jquery.org/style-guide/js/).

### HTML<a name="html"></a>
Like JavaScript HTML is often used for displaying information and as a response for RESTful requests that return an HTML file. Please make an attempt to follow the [jQuery HTML Style Guide](https://contribute.jquery.org/style-guide/html/)

### C<a name="c"></a>
If C is used for Faraday-Software please follow the [GNU Coding Standards](https://www.gnu.org/prep/standards/standards.html) as best as possible.
