from pyfiglet import Figlet
from PyInquirer import prompt
from jinja2 import Template

banner = Figlet(font="slant").renderText("Deploy it")

# Questioning starts
print("Answer the following questions to make your project ready for deployment")

questions = [
    {"type": "input", "name": "django_project_name", "message": "Django project name: "},
    {"type": "input", "name": "username", "message": "What's the username that is being used on the server?"},
    {"type": "input", "name": "working_directory", "message": "Enter absolute path of the project's working directory:"},
    {"type": "input", "name": "venv_path", "message": "Enter the path to your venv folder:"},
    {"type": "input", "name": "wsgi_path", "message": "Enter dot separated WSGI file location:"},
    {"type": "input", "name": "wsgi_app_name", "message": "Name of WSGI app:"}

]

answers = prompt(questions)
print(answers)

print("Generating file...")
with open("gunicorn-template", "r") as f:
    template = Template(f.read())
    print(template.render(answers))


# Run this script with sudo
# Create gunicorn systemd service file
# Create nginx server block file
# Generates the files and places them in the local folder
# Copies the files to the required folder
