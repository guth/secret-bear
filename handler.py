import jinja2
import os
import web

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

class Handler():
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		toRender = self.render_str(template, **kw)
		return toRender

	def redirect(self, path):
		raise web.seeother(path)

	def getParam(self, param):
		return web.input().get(param)

	def setCookie(self, name, value, expires="", domain=None, secure=False):
		web.setcookie(name, value, expires="", domain=None, secure=False)

	def getCookie(self, name):
		return web.cookies().get(name)

	def addResponseHeader(self, name, value):
		web.ctx['headers'].append((name, value))

	def getRequestHeader(self, name):
		return web.ctx.env.get(name)
