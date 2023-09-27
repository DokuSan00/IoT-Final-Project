# To install Flask on Windows, you need Python:

https://www.python.org/downloads/

## Open the *.exe* after finished downloading

Step1: Select "Customize Installation"
Step2: Among 6 checkboxes
	2, 3, 4, 5, 6 must be selected
	Press "Next"
Step3: 7 checkboxes
	1, 2, 4, 5 must be selected
	Press "Install"

Open Command Prompt:
try commands:
	**python --version**
	**pip --version**
both shoulds tell you its version
if not, reinstall and enable every checkboxes

--------------------------------------------------------------

#After Python is installed
##Open Command Prompt to install Flask

to install Flask or use any Python stuffs
you need **python -m** before every command
so, to install Flask, type:
	**python -m pip install Flask**

and follow other environments command using the link:

https://flask.palletsprojects.com/en/2.3.x/installation/

# And things are ready to go. To run a python file, type:

**python -m [file_name]**

where **[file_name]** - what ever file you want to run (**.py**)

In our work, do type:

**python -m app.py**
