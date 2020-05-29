# ChatBot-HappyCall
Chatbot for handling emergency calls
## CONTENTS OF THIS FILE
1. Introduction
2. Requirements
3. Configuration
 
#### INTRODUCTION

- Name:         __HappyCall__
- Authors:
  ```Daniel Casado Faulí``` ```Josep Roig Torres``` ```Joan Carrión Anaya``` 
- Version: __1.0__
- IDE: __Visual Studio Code__

#### REQUIREMENTS
  In order to run this project you need to install the following:

- __Python__:
    - URL: 'https://www.python.org/downloads/'
    - PROJECT VERSION:  __3.8.2__

- __pip__ (Package installer for Python):
    - URL: 'https://pip.pypa.io/en/stable/installing/'
    - PROJECT VERSION:  __20.0.2__
    
    ```
    NOTE
        pip is already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from python.org 
        or if you are working in a Virtual Environment created by virtualenv or pyvenv. 
        Just make sure to upgrade pip.
    ```

- __Django__ (Python Web framework):
    - PROJECT VERSION:  __3.0.5__
     ```
     python -m pip install Django
     ```
     ```
     python -m django --version
     ```
- __MongoDB__ (non-relational database):
    - URL: https://docs.mongodb.com/manual/administration/install-community/

- __Docker__ (Software container):
    - URL: https://www.docker.com/get-started

- __Redis__ (Need docker image):
    ```
    docker run --name some-redis -d redis
    ```

#### CONFIGURATION
  In order to run the server do the following:
  - We will be working in a virtual environment, so in case you don't have installed __venv__ or __virtualenv__, do:
    ```
    (Mac OS / Linux)  python3 -m pip install --user virtualenv
    ```
    ```
    (Windows) python -m pip install --user virtualenv
    ```
  - Once installed, introduce the following commands:
    ```
    >> virtualenv env
    >> (Mac OS / Linux)  source env/bin/activate 
       (Windows)         env\Scripts\activate
    ```      
    
  - Whenever you want to leave the virtual environment do:
    ```
    >> deactivate
    ```

  - Many libraries have been used, in order to have them do the following:
    ```
    pip install -r requirements.txt 
    ```

    ###### IMPORTANT 
    Some errors have been found & fixed during the import, but will appear everytime the project is cloned:
    __To avoid them do the following:__
    - Copy all content from __asyncriorector_fix.py__ ```(Windows) CTRL+A  CTRL+C```
    - Go to __env/Lib/twisted/internet/asyncriorector.py__ and change it with the copy. ```(Windows) CTRL+A  CTRL+V```

  - Because we are using __MongoDB__ to store some information, the following commands need to be done:\
    In the command line, locate yourself in the /src folder:
    ```
    >> cd src
    >> python manage.py makemigrations
    >> python manage.py migrate
    ```
  - Before running the server, we first need to bind Redis to Local port for messaging purpose
    ```
    >> docker run -p 6379:6379 -d redis:5 
    ```
  - Reached this point, everything should be fine to run the server (__Default port:__ 8000)
    ```
    >> python manage.py runserver
    ```
    OR you want to have it in any other port:
    ```    
    python manage.py runserver <server_port> 
    ```
- Finally, to access the ui:
  - http://127.0.0.1:8000/chat
