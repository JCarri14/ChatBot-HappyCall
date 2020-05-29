#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv

def main():
    dotenv.read_dotenv(override=True)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyCall.settings')
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/win/Desktop/PersonalProjects/Python/DjangoChannelsTest/eltelefonodelaalegria-qflysh-411d2ce28cb7.json"
    #os.environ['DIALOGFLOW_PROJECT_ID'] = "bso-agent-kdlbva"
    #os.environ['DIALOGFLOW_PROJECT_ID'] = "eltelefonodelaalegria-qflysh"
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
