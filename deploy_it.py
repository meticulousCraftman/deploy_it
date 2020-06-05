from pyfiglet import Figlet
from PyInquirer import prompt
from jinja2 import Template
import os
import shutil
from pystemd.systemd1 import Unit
import time

os.mkdir("./deploy_it")

banner = Figlet(font="slant").renderText("Deploy it")

# Creating file for gunicorn
print("Answer the following questions to make your project ready for deployment")

gunicorn_questions = [
    {
        "type": "input",
        "name": "django_project_name",
        "message": "Django project name: ",
    },
    {
        "type": "input",
        "name": "username",
        "message": "What's the username that is being used on the server?",
    },
    {
        "type": "input",
        "name": "working_directory",
        "message": "Enter absolute path of the project's working directory:",
    },
    {
        "type": "input",
        "name": "venv_path",
        "message": "Enter the path to your venv folder:",
    },
    {
        "type": "input",
        "name": "wsgi_path",
        "message": "Enter dot separated WSGI file location:",
    },
    {"type": "input", "name": "wsgi_app_name", "message": "Name of WSGI app:"},
]

gunicorn_answers = prompt(gunicorn_questions)
print(gunicorn_answers)

print("Generating file...")
with open("gunicorn-template", "r") as f:
    template = Template(f.read())
    print("Gunicorn service file created!")
    gunicorn_service_file = open("deploy_it/gunicorn.service", "w")
    gunicorn_service_file.write(template.render(gunicorn_answers))
    gunicorn_service_file.close()

# Creating file for Nginx
print("Creating configuration file for Nginx")

nginx_questions = [
    {"type": "input", "name": "server_ip_address", "message": "Server IP address:"},
    {
        "type": "input",
        "name": "static_endpoint",
        "message": "What is the endpoint used to serve static content:",
    },
    {
        "type": "input",
        "name": "staticfile_folder",
        "message": "Absolute path of folder with static assets:",
    },
]

nginx_answers = prompt(nginx_questions)
print(nginx_answers)
nginx_answers.update(gunicorn_answers)

print("Generating file...")
with open("nginx-template", "r") as f:
    template = Template(f.read())
    print("Nginx service file created!")
    nginx_file = open("deploy_it/" + nginx_answers["django_project_name"], "w")
    nginx_file.write(template.render(nginx_answers))
    nginx_file.close()

# Creating a readme file inside deploy_it/ folder
# under the current working directory
with open("deploy_it/README.txt", "w") as f:
    f.write(
        "This folder contains the server configuration file for deploying the django project.\n"
    )
    f.write("And will also contain the log file for the project when it's deployed.")
    f.close()


# Check if systemd folder is present
# Then copy the gunicorn file to that folder
if os.path.exists("/etc/systemd/system/"):
    print("systemd folder found!")
    shutil.copyfile("deploy_it/gunicorn.service", "/etc/systemd/system/gunicorn.service")
else:
    print("systemd folder was not found! Couldn't copy gunicorn.service file.")


# Check if nginx folder is present
# If the folder is present, then copy the nginx server config files
if os.path.exists("/etc/nginx/sites-available/"):
    print("Found nginx folder")
    shutil.copyfile(f"deploy_it/{nginx_answers['django_project_name']}")
else:
    print("Couldn't find nginx configuration folder. Maybe it isn't installed :(")

# Loading the Unit file and starting systemd service
unit = Unit(b'gunicorn.service')
unit.load()
unit.Unit.Start(b'replace')
print("Sleeping for 7 seconds and waiting for gunicorn to start")
time.sleep(7)

# If gunicorn has started, we should see a project_name.sock file
if os.path.exists(nginx_answers["working_directory"]+"/"+nginx_answers["django_project_name"]+".sock"):
    print("Socket file found. Gunicorn has started.")
else:
    print(".sock file not found. Maybe gunicorn wasn't able to start :(")

# Checking nginx config file syntax
