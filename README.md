who-ahqa README
==================

Installing
-----------

1. Install Postgresql from the Postgresql repo - [http://wiki.postgresql.org/wiki/Apt](http://wiki.postgresql.org/wiki/Apt)

    ```
    sudo apt-get install postgresql-9.3 pgadmin3 libpq-dev
    ```

2. Setup the database and database users

    Login as the `postgres` user

    ```
    sudo su - postgres
    ```

    Create the database user

    > Use `whoahqa` as the password when prompted

    ```
    createuser whoahqa -d -P
    ```

    Logout of the postgres user with `exit`

    Create the `dev` database

    ```
    createdb whoahqa_dev -O whoahqa -U whoahqa -h 127.0.0.1
    ```

    Create the `test` database

    ```
    createdb whoahqa_test -O whoahqa -U whoahqa -h 127.0.0.1
    ```

3. Install Virtualenv and make and activate the `virtualenv` for the project

    ```
    sudo pip install virtualenv
    ```

    ```
    virtualenv ~/.virtualenvs/whoahqa --no-site-packages
    ```

    ```
    source ~/.virtualenvs/whoahqa/bin/activate
    ```

4. Clone the repo and change into the project directory and install requirements

    ```
    clone git@github.com:onaio/who-adolescent-hqa.git
    ```
    ```
    cd who-adolescent-hqa
    ```
    ```
    pip install -r requirements.txt
    ```

    Install the requirements in `development` mode

    ```
    python setup.py develop
    ```

5. Migrate the database

    ```
    alembic upgrade head
    ```

6. Run the application

    ```
    pserve development.ini --reload
    ```

Deploy with [Vagrant](http://www.vagrantup.com/)
-------------------

### Installing

1. Download Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. Download Install [Vagrant](http://www.vagrantup.com/downloads.html)

3. Install Ansible, preferably [from source](http://docs.ansible.com/intro_installation.html#running-from-source)

    ```
    cd ~/
    git clone git://github.com/ansible/ansible.git
    cd ./ansible
    source ./hacking/env-setup
    ```
    
    If you don’t have pip installed in your version of Python, install pip (No harm running it if its already installed):
    
    ```
    sudo easy_install pip
    ```
    
    Install Ansible's requirements
    
    ```
    sudo pip install paramiko PyYAML jinja2 httplib2
    ```

4. Load your `terminal` and change into this project's directory

    ```
    cd /path/to/this/directory
    ```

5. Clone the Ona playbooks repo to a different directory
    ```
    git clone git@github.com:onaio/playbooks.git ~/playbooks
    ```

6. Make a symbolic link to the playbooks directory
    ```
    ln -s ~/playbooks ansible
    ```

7. Bring up the virtual machine with Vagrant
    ```
    vagrant up
    ```

    NOTE: This will keep the virtual machine running until you halt it via `vagrant halt`

8. Provision using ansible
    ```
    vagrant provision
    ```

    NOTE: To update to the latest version at any time, run the provision command again.

### Running

1. ssh into the virtual machine
    ```
    vagrant ssh
    ```

2. Change into the project's directory
    ```
    cd /vagrant
    ```

3. Activate the virtual environment
    ```
    source ~/.virtualenvs/whoahqa_dev/bin/activate
    ```

4. Run the server
    ```
    pserve development --reload
    ```

    Load the app in your browser at http://192.168.33.13:6543/clinics/unassigned

    You can now make edits from your host (read OSX) and have them reflected when you refresh the browser.
