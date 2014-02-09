who-ahqa README
==================

Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/initialize_who-ahqa_db development.ini

- $venv/bin/pserve development.ini


Deploy with [Vagrant](http://www.vagrantup.com/)
-------------------

1. Install Vagrant

2. Install Ansible

3. Clone the Ona playbooks repo to a different directory
    ```
    git clone git@github.com:onaio/playbooks.git /some/other/directory
    ```

4. Run Vagrant from within this project's directory
    ```
    cd /this/projects/dir
    vagrant up
    ```

5. Make a symbolic link from tha playbooks directory to ansible within this directory
    ```
    ln -s /path/to/playbooks/repo ansible
    ```

6. Provision using ansible
    ```
    vagrant provision
    ```
