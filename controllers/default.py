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
    form = SQLFORM.factory(Field('query', default=T('Search')))    
    sounds = None
    if form.process(message_onsuccess="").accepted and form.vars.query:
        values = form.vars.query        
        sounds = db(active_sounds).select(orderby=~db.sounds.created_on).find(lambda s: values.lower() in s.title.lower() or values.lower() in s.description.lower() or values.lower() in s.keywords.lower())
    else:
        sounds = db(active_sounds).select(orderby=~db.sounds.created_on)
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
    return dict(form=crud.create(db.sounds, onvalidation=blobstore_upload, next=URL('my_uploads'), message=T('Upload complete!')))

@auth.requires_login()
@auth.requires_signature()
def update_sound():
    return dict(form=crud.update(db.sounds, a0, onvalidation=blobstore_upload, next=URL('my_uploads'), message=T('Upload complete!')))

@auth.requires_login()
@auth.requires_signature()
def delete_sound():
    from google.appengine.ext import blobstore
    sound = db.sounds(a0)
    if not sound:
        raise HTTP(404)
    blobstore.delete_async(sound.blob_key)
    crud.delete(db.sounds, a0, next=URL('my_uploads'), message=T('Sound deleted!'))
    return locals()

@auth.requires_login()
def my_uploads():
    sounds = db(user_sounds).select(orderby=~db.sounds.created_on)
    return locals()

def details():
    detail_sound = db.sounds(a0)    
    if not detail_sound:
        raise HTTP(404)    
    sounds = db(active_sounds & (db.sounds.created_by==detail_sound.created_by)).select(orderby=~db.sounds.created_on)
    return locals()

def user():
    return dict(form=auth())


def download():
    return response.download(request,db)

def download_blob():    
    if request.env.web2py_runtime_gae: 
        from google.appengine.ext import blobstore        
        sound = db.sounds(a0)    
        if not sound:
            raise HTTP(404)
        blob_info = blobstore.BlobInfo.get(sound.blob_key)
        return response.stream(blob_info.open())                
    else:        
        return response.download(request,db)
