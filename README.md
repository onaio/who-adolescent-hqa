[![Build Status](https://travis-ci.org/onaio/who-adolescent-hqa.svg?branch=master)](https://travis-ci.org/onaio/who-adolescent-hqa)

# WHO-AHQA README

This project was built by Ona Systems Inc for the Brazilian Ministry of Health and the World Health Organization.

## Installing

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
    git clone git@github.com:onaio/who-adolescent-hqa.git
    ```
    ```
    cd who-adolescent-hqa
    ```
    ```
    pip install -r requirements.txt
    ```

    > If you are on macOS and see the above fail with "error linking uwsgi" try running
    >
    > ```
    > CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -Iv
    > ```

    > Then rerun the previous command.

    Install the requirements in `development` mode

    ```
    python setup.py develop
    ```

5. Migrate the database

    ```
    alembic upgrade head
    ```

6. Set the credentials in `development.ini`

   > All credentials with `REPLACE_ME` as their value should be set to the appropriate values for your installation.
   >
   > You may also need to set the credentials in `production.ini` and `test.ini`

7. Run the application

    ```
    pserve development.ini --reload
    ```

## Deployment

Execute the following command to deploy from the dev host server

### Stage

```
ansible-playbook -i inventory/ona-whoahqa-stage.ini whoahqa.yaml -vvvv --extra-vars="git_branch=master env_settings=production instance_ids=['i-02e706da7a3c850b0']" --vault-password-file ~/.vault_pass.txt
```

### Production

```
ansible-playbook -i inventory/ona-whoahqa.ini whoahqa.yaml -vvvv --extra-vars="git_branch=master env_settings=production instance_ids=['i-02e706da7a3c850b0']" --vault-password-file ~/.vault_pass.txt
```

### NOTE

Before running the app or tests, you need to add

```
export WHOAHQA_COUNTRY_SETTING=whoahqa.constants.brazil_characteristics
```
to your `~/.bashrc` or `~/.zshrc` file.

## Licenese

All code is provided under the Apache 2 license.
