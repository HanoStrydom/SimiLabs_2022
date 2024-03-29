# SimiLabs 2022
**A plagiarism/stylometry checker using Python**
____________________________________________________________
Powered by:
[![N|Solid](https://codersera.com/blog/wp-content/uploads/2019/06/flask-1.png)](https://flask.palletsprojects.com/en/2.1.x/)



# Meet the NightCore Mech team:
| Name | Role |
| ------ | ------ |
| [Ricus Warmenhoven] | Project Manager |
| [Hanno Visagie] | Project Leader (Extensive Text)|
| [Hano Strydom] | Full Stack Developer (Quick Text)|
| [Llewellyn Anthony] | Development Lead (Quick Text)|
| [Michael Rosin] | Back-end Lead (Stylometry)|
| [Annika du Toit] | Back-end Developer (Extensive Text) |
| [Shené Boshoff] | Back-end Developer (Stylometry)|

# SimiLabs Goal
The current requirements from the client (NWU Registrar), with Mr Zander Janse van Rensburg as the project overseeing manager, requires our company to design and build a modular workflow system that would assist lecturers in academics to identify and report academic misconduct cases according to standing NWU SOPS. The NWU Registrar must address plagiarism by evaluating each case individually and appointing experts to prepare technical reports. 

# Packages
- Download and install the lastest version of [Python]
- Download and install the lastest version of [Visual Studio Code]
- Before executing the development commands, import this packages:
```sh
pip install .
or
cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 python -m pip install
```
> Requirements can also be seen in the requirements.txt document.

# Database
- Download and install the lastest version of [MySQL] (mysql-installer-community-8.0.31.0.msi)
- Create a SimiLabs [MySQL] connection
- Create an 'accounts' table and insert the Admin user
```sh
See the Technical User Manual for a more detailed overview of the installation and setup
```


# Development
Before executing flask, the following commands needs to be run in [GitBash]: 

> Git Bash is an application for Microsoft Windows environments which provides an emulation layer for a Git command line experience. Bash is an acronym for Bourne Again Shell. A shell is a terminal application used to interface with an operating system through written commands

*For older flask versions*
```sh
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```
*For newer flask versions*
```sh
export FLASK_APP=example
export FLASK_DEBUG=1
flask run
```

# Documentation
- [Documentation]
- [User Manual]
- [Developer Manual]


## License
- MIT

*Copyright (c) 2022 ISE-Project-2022*

*Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:*

*The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.*

*THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.*



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen.)

   [Ricus Warmenhoven]: <mailto: ricusw@gmail.com>
   [Hanno Visagie]: <mailto: hanno.visagie.16@gmail.com>
   [Hano Strydom]: <mailto: hanostrydom8@gmail.com>
   [Llewellyn Anthony]: <mailto: llewellynant@gmail.com>
   [Michael Rosin]: <mailto: michaeljoshuarosin@gmail.com>
   [Annika du Toit]: <mailto: nikadt.42@gmail.com>
   [Shené Boshoff]: <mailto: sheneboshoff6@gmail.com>
   [GitBash]: <https://git-scm.com/downloads>
   [Documentation]: <https://github.com/ISE-Project-2022/Documentation>
   [User Manual]: <https://github.com/ISE-Project-2022/Documentation/blob/main/SimiLabs_User_Manual_V1.1.pdf>
   [Developer Manual]: <https://github.com/ISE-Project-2022/Documentation/blob/main/Developer_Manual_NightcoreMech_V1.1.pdf>
   [python]: <https://www.python.org/downloads/>
   [Visual Studio Code]: <https://code.visualstudio.com/download>
   [MySQL]: <https://dev.mysql.com/downloads/installer/>
   


