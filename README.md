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
    git clone git@github.com:onaio/who-adolescent-hqa.git
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

Deploy to AWS
-------------------
Execute the following command to deploy from the dev host server

### NOTE

Before running the app or tests, you need to add

```
export WHOAHQA_COUNTRY_SETTING=whoahqa.constants.brazil_characteristics
```
to your `~/.bashrc` or `~/.zshrc` file.
