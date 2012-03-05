# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():    
    sounds = db(db.sounds).select()
    return locals()

@auth.requires_login()
def upload():
    return dict(form=crud.update(db.sounds, a0))

def details():
    sound = db.sounds(a0)
    if not sound:
        raise HTTP(404)
    user = db.auth_user(sound.created_by)
    if not user:
        user = T("Annonimous")
    else:
        user = user.first_name + " " + user.last_name
    return locals()

def user():
    return dict(form=auth())


def download():
    return response.download(request,db)
