import os
import shutil
import subprocess
import time
import pwd
import pathlib

from PyInquirer import prompt
from jinja2 import Template
from pyfiglet import Figlet
from pystemd.systemd1 import Unit
from halo import Halo

spinner = Halo()


def initialization():
    if not os.path.exists("deploy_it/"):
        os.mkdir("./deploy_it")
    banner = Figlet(font="slant").renderText("Deploy it")
    print(banner)


def gunicorn_config():
    def validate_django_project_name(project_name):
        if len(project_name) > 0:
            return True
        return "Django project name cannot be blank."

    def validate_username(username):
        username = username.strip()
        try:
            pwd.getpwnam(username)
            return True
        except KeyError:
            return "Specified user was not found. Please enter the correct username."

    def validate_venv_path(venv_raw_path):
        path = pathlib.Path(venv_raw_path)

        # Assuming the venv has been created using virutalenv
        path = path / "bin" / "activate"

        # Check if the bin/activate file exists?
        if path.exists():
            return True

        return f"Unable to find a virtual env at {str(path)}. Please check the path (Only virtualenv env's supported)"

    def validate_wsgi_path(raw_wsgi_path):
        wsgi_path = raw_wsgi_path

        # Create path to the file
        wsgi_path = wsgi_path.split(".")
        wsgi_path[-1] = wsgi_path[-1]+".py"
        wsgi_path = "/".join(wsgi_path)
        path = pathlib.Path(wsgi_path)
        if path.exists():
            return True
        return f"Unable to find wsgi file at {path}"

    def validate_wsgi_app_name(wsgi_app_name):
        if len(wsgi_app_name) > 0:
            return True

        return "WSGI application cannot be blank."

    # Creating file for gunicorn
    spinner.info(
        "Answer the following questions to make your project ready for deployment"
    )

    gunicorn_questions = [
        {
            "type": "input",
            "name": "django_project_name",
            "message": "Django project name: ",
            "validate": validate_django_project_name,
        },
        {
            "type": "input",
            "name": "username",
            "message": "What's the username that is being used on the server?",
            "validate": validate_username,
        },
        {
            "type": "input",
            "name": "venv_path",
            "message": "Enter virtual environment folder name (or absolute path):",
            "validate": validate_venv_path,
        },
        {
            "type": "input",
            "name": "wsgi_path",
            "message": "Enter dot separated WSGI file location with respect to current working directory (eg: config.wsgi):",
            "validate": validate_wsgi_path,
        },
        {
            "type": "input",
            "name": "wsgi_app_name",
            "message": "Name of WSGI app:",
            "validate": validate_wsgi_app_name,
        },
    ]

    gunicorn_answers = prompt(gunicorn_questions)
    return gunicorn_answers


def generate_gunicorn_config_file(config):
    print("Generating file...")
    with open("gunicorn-template", "r") as f:
        template = Template(f.read())
        print("Gunicorn service file created!")
        gunicorn_service_file = open("deploy_it/gunicorn.service", "w")
        gunicorn_service_file.write(template.render(config))
        gunicorn_service_file.close()


def nginx_config():
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
    return nginx_answers


def generate_nginx_config_file(config):
    print("Generating file...")
    with open("nginx-template", "r") as f:
        template = Template(f.read())
        print("Nginx service file created!")
        nginx_file = open("deploy_it/" + config["django_project_name"], "w")
        nginx_file.write(template.render(config))
        nginx_file.close()


# Creating a readme file inside deploy_it/ folder
# under the current working directory
def generate_readme():
    with open("deploy_it/README.txt", "w") as f:
        f.write(
            "This folder contains the server configuration file for deploying the django project.\n"
        )
        f.write(
            "And will also contain the log file for the project when it's deployed."
        )
        f.close()


# Check if systemd folder is present
# Then copy the gunicorn file to that folder
def register_gunicorn_service(nginx_answers):
    service_registered = False
    try:
        if os.path.exists("/etc/systemd/system/"):
            print("systemd folder found!")
            shutil.copyfile(
                "deploy_it/gunicorn.service", "/etc/systemd/system/gunicorn.service"
            )
            service_registered = True
        else:
            print("systemd folder was not found! Couldn't copy gunicorn.service file.")
    except PermissionError:
        spinner.fail(
            "The script does not has the permission to copy files /etc/systemd/system/ folder."
        )
        spinner.info(
            "You have to manually copy the gunicorn.service file to /etc/systemd/system/ folder."
        )

    if service_registered:

        # Loading the Unit file and starting systemd service
        unit = Unit(b"gunicorn.service")
        unit.load()
        unit.Unit.Start(b"replace")
        spinner.info("Sleeping for 7 seconds and waiting for gunicorn to start")
        time.sleep(7)

        # If gunicorn has started, we should see a project_name.sock file
        if os.path.exists(
            nginx_answers["working_directory"]
            + "/"
            + nginx_answers["django_project_name"]
            + ".sock"
        ):
            spinner.succeed("Socket file found. Gunicorn has started.")
        else:
            spinner.fail(
                "gunicorn.sock file not found. Maybe gunicorn wasn't able to start :("
            )


# Check if nginx folder is present
# If the folder is present, then copy the nginx server config files
def register_nginx_config_file(nginx_answers):
    service_registered = False

    try:
        if os.path.exists("/etc/nginx/sites-available/"):
            print("Found nginx folder")
            shutil.copyfile(f"deploy_it/{nginx_answers['django_project_name']}")
            service_registered = True
        else:
            print(
                "Couldn't find nginx configuration folder. Maybe it isn't installed :("
            )
    except PermissionError:
        spinner.fail(
            "Unable to copy nginx config file. You have to manually copy the file."
        )

    if service_registered:
        # Creating a soft link to sites-available
        subprocess.Popen(
            [
                "sudo",
                "ln",
                "-s",
                f"/etc/nginx/sites-available/{nginx_answers['django_project_name']}",
                "/etc/nginx/sites-enabled",
            ]
        )

        if os.path.exists(
            f"/etc/nginx/sites-enabled/{nginx_answers['django_project_name']}"
        ):
            print("Nginx config file link created to sites-enabled")
        else:
            print("Unable to create a link of nginx config file to sites-enabled")

        # Checking nginx config file syntax
        out = subprocess.Popen(
            ["sudo", "nginx", "-t"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = out.communicate()

        if stderr is None:
            print("nginx file seems to be just fine :)")
        else:
            print("There is some problem in the generated nginx config file")


def parse_user_input(config):
    config["working_directory"] = os.getcwd()
    return config


# restart nginx
# enable nginx to pass through the firewall


def main():
    # Initialize the current working directory by creating deploy_it/ folder
    # ask questions to create the gunicorn config file
    # Finally, generate the config file
    initialization()
    gconfig = gunicorn_config()
    generate_gunicorn_config_file(gconfig)

    # ask questions for creating nginx config file
    # generate nginx config file
    nconfig = nginx_config()
    nconfig.update(gconfig)
    generate_nginx_config_file(nconfig)

    # Add whatever extra keys have to be added to this dictionary
    nconfig = parse_user_input(nconfig)

    # register gunicorn service file in systemd
    register_gunicorn_service(nconfig)
    # register nginx config file under
    register_nginx_config_file(nconfig)

    # Generate readme file under deploy_it folder
    generate_readme()


if __name__ == "__main__":
    main()
