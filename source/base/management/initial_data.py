
'''
	create initial data for this model, on syncdb
	make sure to check if it doesn't yet exist
'''

from admin_settings import Setting
from statix.models.page import Page


INITIAL_USER = 'mark.verleg@gmail.com'

def initial_data(verbosity, *args, **kwargs):
	'''
		initialize display parameters (as settings)
	'''
	if not Setting.objects.filter(name = 'TITLE_BASE'):
		Setting(name = 'TITLE_BASE', value = '(change in admin)', explanation = 'the base part of the title of pages', type = Setting.STR, template = 2).save()
		Setting(name = 'TITLE_SEPARATOR', value = '&laquo;', explanation = 'the base part of the title of pages', type = Setting.STR, template = 2).save()
		if verbosity:
			print 'created display settings'
	'''
		initialize pages
	'''
	if not Page.objects.filter(path = 'credits'):
		Page(path = 'credits', title = 'Credits', content = '''
			<h1>Credits</h1>
			<p>This website was made possible by materials from various sources. Gratitude is due for making this project possible! These include, in any orders:</p>
			<ul>
				<li>Python: the server-side language <a href="https://www.python.org/">python.org</a></li>
				<li>Django: the web development framework <a href="https://www.djangoproject.com/">djangoproject.com</a></li>
				<li>jQuery: client-side library for javascript <a href="http://jquery.com/">jquery.com</a></li>
				{# #todo #}
			</ul>
		'''.replace('\t', '')).save()
		if verbosity:
			print 'created credits page'
	if not Page.objects.filter(path = 'contact'):
		Page(path = 'contact', title = 'Contact', content = '''
			{% load ext %}
			<h1>Contact</h1>
			<p>Feel free to contact us; we can be reached in many ways:</p>
			<p>Email: {{ "company@spam.la"|obfuscate }}</p>
			<p>Phone: 06 1234 5678</p>
			<p>Address: etc etc</p>
			<p>Messenger pigeon: on Wednesday, have your pigeon deliver your message in the garden of aforementioned address, if weather allows</p>
		'''.replace('\t', '')).save()
		if verbosity:
			print 'created contact page'
	if not Page.objects.filter(path = 'about'):
		Page(path = 'about', title = 'About', content = '''
			{% load statix_tags %}
			<h1>About</h1>
			<p>We are the best ones!</p>
		'''.replace('\t', '')).save()
		if verbosity:
			print 'created about page'

