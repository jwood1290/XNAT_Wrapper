import logging
from pyxnat import Interface
from .utils import format_err
from .uid_importer import UIDImporter
from .command_utility import CommandUtility


class Connector(object):
	'''Class that provides methods to connect to an XNAT instance. 
	Either pass the `config` parameter by itself or pass each of 
	the `server`, `user`, and `password` parameters.

	:param str config: The name of the XNAT login config file
	:param str server: The XNAT server IP address
	:param str user: The username for the XNAT session
	:param str password: The password for the XNAT session
	:param project: The name of an XNAT project
	:type project: str, optional
	'''

	def __init__(self, **kwargs):
		'''Constructor method
		'''

		self.xnat = None
		self.project = None
		self.importer = None
		self.commands = None

		self._login = None
		self._uptime = None
		self._is_connected = False

		self.initialize_session(**kwargs)

	def initialize_session(self, **kwargs):
		'''Creates an XNAT interface that can be used to interact 
		with projects, sessions, and scans.

		:param str config: The name of the XNAT login config file
		:param str server: The XNAT server IP address
		:param str user: The username for the XNAT session
		:param str password: The password for the XNAT session
		:param project: The name of an XNAT project
		:type project: str, optional
		'''

		if self.xnat is not None:
			try:
				self.close_session()
			except: pass

		if 'config' in kwargs:
			self._login = {'config':kwargs['config']}
		else:
			self._login = {k:v for k,v in kwargs.items() if k in ['server','user','password']}

		if 'project' in kwargs: self.project = kwargs['project']

		try:
			self.xnat = Interface(**self._login)
			self.importer = UIDImporter(self.xnat, self.project)
			self.commands = CommandUtility(self.xnat, self.project)
		except Exception as ex:
			format_err(ex)

	def close_session(self):
		'''Disconnects from the current XNAT session
		'''

		self.xnat.disconnect()
		self.xnat = None
		self.importer = None
		self.commands = None
		self._is_connected = False

	def set_project(self, project):
		'''Sets the project for entire XNAT connection 
		(importer and command utilites included).

		:param str project: The name of the XNAT project
		'''

		self.project = project
		self.importer.set_project(project)
		self.commands.set_project(project)

	def is_connected(self):
		'''Checks for a valid XNAT connection

		:return: `True` if there is a valid XNAT connection, else `False`
		:rtype: bool
		'''

		self._is_connected = False
		if self.xnat is not None: 
			try:
				res = self.xnat.get('/xapi/siteConfig/uptime/display')
				res.raise_for_status()
				self._uptime = res.text
				self._is_connected = True
			except: pass

		return self._is_connected

	def get_uptime(self):
		'''Returns the server uptime as a string

		:return: Amount of time the server has been online
		:rtype: str
		'''

		if self.is_connected():
			return self._uptime
		else:
			return 'WARNING: XNAT server is offline'


if __name__ == '__main__': 
	pass