import os
from fabric.api import cd, run, env, prefix

DEPLOYMENTS = {
    'prod': {
        'host_string': "ubuntu@whoahqa.ona.io",
        'virtual_env': '/home/ubuntu/.virtualenvs/whoahqa_prod',
        'test_virtual_env': '/home/ubuntu/.virtualenvs/whoahqa_test',
        'project_dir': '/home/ubuntu/whoahqa',
        'alembic_section': 'production',
        'country': 'brazil'
    },
    'dev': {
        'host_string': "vagrant@192.168.33.13",
        'virtual_env': '/home/vagrant/.virtualenvs/whoahqa_dev',
        'test_virtual_env': '/home/vagrant/.virtualenvs/whoahqa_test',
        'project_dir': '/home/vagrant/whoahqa'
    }
}


def get_virtual_env_command(virtual_env_path):
    return 'source {}'.format(
        os.path.join(virtual_env_path, 'bin', 'activate'))


def deploy(deployment="prod", branch="master", country=None):
    env.update(DEPLOYMENTS[deployment])
    virtual_env_command = get_virtual_env_command(env.virtual_env)
    with cd(env.project_dir):
        run("git checkout {branch}".format(branch=branch))
        run("git pull origin {branch}".format(branch=branch))
        run('find . -name "*.pyc" -exec rm -rf {} \;')

        with prefix(virtual_env_command):
            run('pip install -r requirements.txt --allow-all-external')
            run('export WHOAHQA_COUNTRY_SETTING={}'.format(
                country or env.get('country')))
            run("python setup.py test -q")
            run("python setup.py install")
            run("rm -rf build")
            # run migrations
            run("alembic -n {0} upgrade head".format(
                env.get('alembic_section', 'alembic')))
            run("python setup.py compile_catalog")

            run("uwsgi --reload /var/run/whoahqa.pid")
