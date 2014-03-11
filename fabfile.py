import os
from fabric.api import local, cd, run, settings, env, prefix

DEPLOYMENTS = {
    'prod': {
        'host_string': "ubuntu@whoahqa.ona.io",
        'virtual_env': '/home/ubuntu/.virtualenvs/whoahqa_prod',
        'project_dir': '/home/ubuntu/whoahqa',
        'alembic_section': 'production'
    },
    'dev': {
        'host_string': "vagrant@192.168.33.13",
        'virtual_env': '/home/vagrant/.virtualenvs/whoahqa_dev',
        'project_dir': '/home/vagrant/whoahqa'
    }
}


def test(branch="master"):
    local("git checkout %s" % branch)
    local("python setup.py test -q")


def deploy(deployment="prod", branch="master"):
    env.update(DEPLOYMENTS[deployment])
    virtual_env_command = 'source {}'.format(
        os.path.join(env.virtual_env, 'bin', 'activate'))
    test(branch)
    with cd(env.project_dir):
        run("git checkout {branch}".format(branch=branch))
        run("git pull origin {branch}".format(branch=branch))

        # run migrations
        with prefix(virtual_env_command):
            run("python setup.py install")
            run("alembic -n {0} upgrade head".format(
                env.get('alembic_section', 'alembic')))
            run("python setup.py extract_messages")
            run("python setup.py compile_catalog")

    # Reload uWSGI
    run("/usr/local/bin/uwsgi --reload /var/run/whoahqa.pid")
