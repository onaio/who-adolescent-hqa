who-ahqa README
==================

Deploy with [Vagrant](http://www.vagrantup.com/)
-------------------

### Installing

1. Download Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. Download Install [Vagrant](http://www.vagrantup.com/downloads.html)

3. Install Ansible. Preferably [from source](http://docs.ansible.com/intro_installation.html#running-from-source)

4. Load your `terminal` and change into this project's directory

    ```
    cd /path/to/this/directory
    ```

5. Clone the Ona playbooks repo to a different directory
    ```
    git clone git@github.com:onaio/playbooks.git /some/other/directory/playbooks
    ```

6. Make a symbolic link to the playbooks directory
    ```
    ln -s /some/other/directory/playbooks ansible
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
