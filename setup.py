import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.5',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'alembic',
    'psycopg2',
    'fabric',
    'python-slugify',
    'pyramid_jinja2',
    'WebTest',
    'alembic',
    'requests',
    'requests-oauthlib',
    'httmock',
    'hashids',
    'nose',
    'coverage',
    'pyramid_exclog',
    'pyenketo',
    'Babel',
    'lingua',
    'passlib',
    'colander',
    'deform',
    'flake8'
]

extractors = {
    'whoahqa': [
        ('**.py', 'lingua_python', None),
        ('**.jinja2', 'jinja2', None)
    ]
}

setup(name='who-ahqa',
      version='0.1a',
      description='WHO Adolescent Health Quality Assessment',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Ona Labs',
      author_email='support@ona.io',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='whoahqa',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = whoahqa:main
      [console_scripts]
      initialize_who-ahqa_db = whoahqa.scripts.initializedb:main
      create_whoahqa_user = whoahqa.scripts.create_user:main
      parse_municipalities = whoahqa.scripts.submission_parser:main
      """,
      message_extractors=extractors
      )
