# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = ' SonicaLabs'
response.subtitle = T('Experience THE EXPERIENCE')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Radu Fericean <radu.fericean@wisebiz-group.com>'
response.meta.description = 'SonicaLabs is a webapp for sounds/audio storage and presentation'
response.meta.keywords = 'audio, sound, music, record sound, sharing'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default','index'), [])
    ]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu+=[
        (SPAN('Explore',_style='color:yellow'),False, None, [
                (T('Upload a file'),False,URL('default','upload')),
                (T('Record a sound'),False,URL('default','record')),
                (T('My uploads'),False,URL('default','my_uploads')),
                ]
         )]
_()

