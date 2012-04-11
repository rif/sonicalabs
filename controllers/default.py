# -*- coding: utf-8 -*-
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo

def index():
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate,  extra_vars={'v':1}, anchor='main', renderstyle=True) 
    paginator.records = db(active_sounds).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)
    
    form = SQLFORM.factory(Field('query', default=T('Search')))    
    
    sounds = None
    if form.process(message_onsuccess="").accepted and form.vars.query:
        values = form.vars.query        
        sounds = db(active_sounds).select(orderby=~Sounds.created_on,
            limitby=paginator.limitby()).find(lambda s: values.lower() in s.title.lower() or values.lower() in s.description.lower() or values.lower() in s.keywords.lower())
    else:
        sounds = db(active_sounds).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
    return locals()

@auth.requires_login()
def record():
    return locals()


def blobstore_upload(form):        
    if request.env.web2py_runtime_gae and form.vars.file is not None and form.vars.file != '':        
        from google.appengine.api import files
        from google.appengine.ext import blobstore
        # Create the file        
        file_name = files.blobstore.create(mime_type='application/octet-stream', _blobinfo_uploaded_filename=form.vars.file.filename)        
        # Open the file and write to it
        with files.open(file_name, 'a') as f:            
            f.write(form.vars.file.file.read())

        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)

        # Get the file's blob key        
        form.vars.blob_key = files.blobstore.get_blob_key(file_name)        
        form.vars.file = None        

@auth.requires_login()
def create_sound():
    form = SQLFORM(Sounds)        
    if form.process().accepted:
        new_sound = Sounds(form.vars.id)
        if not new_sound.title and request.vars.file != None:                
            new_sound.update_record(title = request.vars.file.filename)
        response.flash = T('Upload complete!')
        redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
       response.flash = T('form has errors') 
    return locals()

@auth.requires_login()
@auth.requires_signature()
def update_sound():    
    sound = Sounds(a0) or redirect(URL('index'))
    form = SQLFORM(Sounds, sound, fields=['title', 'description', 'keywords', 'language', 'price'], showid=False)
    if form.process().accepted:
       response.flash = T('Sound info updated!')
       redirect(URL('my_uploads', user_signature=True))
    elif form.errors:
       response.flash = T('form has errors')    
    return locals()

@auth.requires_login()
@auth.requires_signature()
def delete_sound():    
    if request.env.web2py_runtime_gae:
        from google.appengine.ext import blobstore
        sound = Sounds(a0) or redirect(URL('index'))
        blobstore.delete_async(sound.blob_key)
    crud.delete(Sounds, a0, next=URL('my_uploads', user_signature=True), message=T('Sound deleted!'))
    return locals()

@auth.requires_login()
@auth.requires_signature()
def my_uploads():    
    paginator = Paginator(paginate=10, extra_vars={'v':1}, anchor='main', renderstyle=True) 
    paginator.records = db(user_sounds).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    sounds = db(user_sounds).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
    return locals()

def details():    
    detail_sound = Sounds(a0) or redirect(URL('index'))   
    query = active_sounds & (Sounds.created_by==detail_sound.created_by)
    new_count = detail_sound.play_count or 0 + 1
    detail_sound.update_record(play_count=new_count)

    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate, extra_vars={'v':1}, anchor='main', renderstyle=True) 
    paginator.records = db(query).count()
    paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)

    sounds = db(query).select(orderby=~Sounds.created_on, limitby=paginator.limitby())
    return locals()

def most_popular():        
    paginate_selector = PaginateSelector(anchor='main')
    paginator = Paginator(paginate=paginate_selector.paginate, extra_vars={'v':1}, anchor='main', renderstyle=True) 
    paginator.records = db(active_sounds).count()    

    sounds = db(active_sounds).select(orderby=~Sounds.play_count, limitby=paginator.limitby())
    return locals()

def user():
    return dict(form=auth())


def download():
    return response.download(request,db)

def download_blob():    
    if request.env.web2py_runtime_gae: 
        from google.appengine.ext import blobstore        
        sound = Sounds(a0) or redirect(URL('index'))
        blob_info = blobstore.BlobInfo.get(sound.blob_key)
        return response.stream(blob_info.open())                
    else:        
        return response.download(request,db)

def about():
    return dict()

def terms():
    return dict()

def howitworks():
    return dict()

def contact():   
    form=SQLFORM.factory(
        Field('your_name',requires=IS_NOT_EMPTY()),
        Field('your_email',requires=IS_EMAIL()),
        Field('message', 'text', requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        if mail.send(to='radu.fericean@wisebiz-group.com;gmurgan@sympatico.ca;teodor.giles@wisebiz-group.com',
                  subject='from %s (%s)' % (form.vars.your_name, form.vars.your_email),
                  message = form.vars.message):
            response.flash = 'Thank you'
            response.js = "jQuery('#%s').hide()" % request.cid
        else:
            form.errors.your_email = "Unable to send the email"
    return dict(form=form)

def buy():
    return dict()
