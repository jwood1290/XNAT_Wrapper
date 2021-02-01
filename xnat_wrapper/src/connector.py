from pyxnat import Interface
from src.utils import format_err
from src.uid_importer import UIDImporter
from src.command_utility import CommandUtility


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

		self.initialize_session(**kwargs)
		self.importer = UIDImporter(self.xnat, self.project)
		self.commands = CommandUtility(self.xnat, self.project)

	def initialize_session(self, **login):
		'''Creates an XNAT interface that can be used to interact 
		with projects, sessions, and scans.

		:param dict login: A dictionary containing a config file or server, user, and password
		'''

		if self.xnat is not None:
			try:
				self.close_session()
			except: pass

		try:
			valid_keys = ['server','user','password','config']
			login = {k:v for k,v in login.items() if k in valid_keys}
			self.xnat = Interface(**login)

			if 'project' in kwargs: self.project = project
		except Exception as ex:
			format_err(ex)

	def close_session(self):
		'''Disconnects from the current XNAT session
		'''

		self.xnat.disconnect()
		self.xnat = None

	def set_project(self, project):
		'''Sets the project for entire XNAT connection 
		(importer and command utilites included).

		:param str project: The name of the XNAT project
		'''

		self.project = project
		self.importer.set_project(project)
		self.commands.set_project(project)



if __name__ == '__main__': 
	pass