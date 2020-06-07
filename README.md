# Deploy It
Deploy your django apps just by running one single command.

## Dependencies

  - nginx
  - gunicorn
  - debian based system
  - apt package manager
  - systemd program
  - postgresql (future)
  - libsystemd-dev (sudo apt install libsystemd-dev, required for pystemd)
  - python >=3.6

## Usage
 There are multiple ways to use **deploy_it**. We recommend using pipx, it's cleaner that way :)

## Run without installing - pipx run 
 ```commandline
$ pipx run deploy_it
``` 
The best thing about this command is that nothing gets installed on your system!
pipx downloads the package from PyPI and just runs it for you. Once you are done
with the application, it removes the application.

### Install and run - pipx
```commandline
$ pipx install deploy_it
$ deploy_it
```

### Standard way
```commandline
$ pip install deploy_it
$ deploy_it
```