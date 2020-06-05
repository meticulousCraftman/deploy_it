from pyfiglet import Figlet
from PyInquirer import prompt
from jinja2 import Template

banner = Figlet(font="slant").renderText("Deploy it")

# Creating file for gunicorn
print("Answer the following questions to make your project ready for deployment")

gunicorn_questions = [
    {"type": "input", "name": "django_project_name", "message": "Django project name: "},
    {"type": "input", "name": "username", "message": "What's the username that is being used on the server?"},
    {"type": "input", "name": "working_directory", "message": "Enter absolute path of the project's working directory:"},
    {"type": "input", "name": "venv_path", "message": "Enter the path to your venv folder:"},
    {"type": "input", "name": "wsgi_path", "message": "Enter dot separated WSGI file location:"},
    {"type": "input", "name": "wsgi_app_name", "message": "Name of WSGI app:"}

]

gunicorn_answers = prompt(gunicorn_questions)
print(gunicorn_answers)

print("Generating file...")
with open("gunicorn-template", "r") as f:
    template = Template(f.read())
    print("Gunicorn service file created!")
    gunicorn_service_file = open("gunicorn.service", "w")
    gunicorn_service_file.write(template.render(gunicorn_answers))
    gunicorn_service_file.close()

# Creating file for Nginx
print("Creating configuration file for Nginx")

nginx_questions = [
    {"type": "input", "name": "server_ip_address", "message": "Server IP address:"},
    {"type": "input", "name": "static_endpoint", "message": "What is the endpoint used to serve static content:"},
    {"type": "input", "name": "staticfile_folder", "message": "Absolute path of folder with static assets:"},
]

nginx_answers = prompt(nginx_questions)
print(nginx_answers)

print("Generating file...")
with open("nginx-template", "r") as f:
    nginx_answers.update(gunicorn_answers)
    template = Template(f.read())
    print("Nginx service file created!")
    nginx_file = open(nginx_answers['django_project_name'], "w")
    nginx_file.write(template.render(nginx_answers))
    nginx_file.close()

# Run this script with sudo
# Create gunicorn systemd service file
# Create nginx server block file
# Generates the files and places them in the local folder
# Copies the files to the required folder