# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:    
    db = DAL('sqlite://storage.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'sonicalbs@gmail.com'
mail.settings.login = 'ustest:greta.1'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

# if request.env.web2py_runtime_gae:            # if running on Google App Engine
#     from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
#     auth.settings.login_form = GaeGoogleAccount()    
#     #auth.settings.actions_disabled.append('profile')


def get_username(row):
    u = db.auth_user(row.sounds.created_by)
    return u.first_name + ' ' + u.last_name if u else T("Anonymous")


db.define_table("sounds",
    Field('title', required=True, requires=IS_NOT_EMPTY()),
    Field('description', 'text'),
    Field('keywords', comment=T('Comma separated key words')),
    Field('blob_key', writable=False, readable=False),
    Field('file', 'upload', requires=IS_UPLOAD_FILENAME(extension='mp3', error_message=T('Please upload an mp3 file')), comment=T('MP3 file. 10Mb size limit.')),
    Field('language', 'list:string', requires=IS_IN_SET(('Română','English','Deutsch')), default='English'),
    Field('price', 'double', default=0.0, comment='$USD'),
    Field('length', 'double', writable=False, readable=False),
    Field('play_count', 'integer', readable=False, writable=False, default=0),
    Field('release_date', 'date', comment=T('Select a date to release this recording in the future')),
    Field('email', requires = IS_EMPTY_OR(IS_EMAIL(error_message=T('Invalid email!'))), comment=T('Email to be sent to (the release notification)')),
    auth.signature,
    format='%(title)s'
)
db.sounds.mime_type = Field.Virtual(lambda row: 'audio/mpeg') #'audio/ogg' if row.sounds.file.rsplit('.', 1)[-1] == 'ogg' else 'audio/mpeg')
db.sounds.username = Field.Virtual(get_username)

a0,a1 = request.args(0), request.args(1)
active_sounds = db.sounds.is_active == True
user_sounds = db.sounds.created_by == auth.user_id