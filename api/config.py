import os

basedir = os.path.abspath(os.path.dirname(__file__))

env_vars = dict(os.environ)

CSRF_ENABLED = True
SECRET_KEY = env_vars['API_SECRET_KEY']
SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%d/%s' % \
(env_vars['POSTGRES_USERNAME'], env_vars['POSTGRES_PASSWORD'], env_vars['POSTGRES_HOST'],
 int(env_vars['POSTGRES_PORT']), env_vars['POSTGRES_DB'])
