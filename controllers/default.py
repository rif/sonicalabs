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
    form = SQLFORM.factory(Field('query', default=T('Search')), _action=URL('search'))        
    return locals()

def search():
    form = SQLFORM.factory(Field('query', default=T('Search')), _action=URL('search'))
    query = db.sounds
    if form.process().accepted and form.vars.query:
        values = form.vars.query.split(' ')        
        query = db.sounds.title.contains(values, False)
        query |= db.sounds.description.contains(values, False)            
    sounds = db(query).select()
    return response.render('default/index.html', locals())

@auth.requires_login()
def upload():
    return dict(form=crud.update(db.sounds, a0))

def details():
    sound = db.sounds(a0)
    if not sound:
        raise HTTP(404)
    user = db.auth_user(sound.created_by)
    if not user:
        user = T("Anonymous")
    else:
        user = user.first_name + " " + user.last_name
    return locals()

def user():
    return dict(form=auth())


def download():
    return response.download(request,db)
