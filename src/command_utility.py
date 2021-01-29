import json
import logging
from src.utils import (
	format_err, 
	write_json
)


class CommandUtility(object):
	'''Class that provides methods to run commands on XNAT projects, 
	sessions, and scans.

	:param class xnat: An open XNAT connection via pyxnat.Interface()
	:param project: Name of the XNAT project, defaults to None
	:param commands: Dictionary of commands with the XNAT project level 
		(i.e. project, session, or scan) as the keys and the command 
		name and options as the values.
	:param scans: A list of XNAT project scans
	:param sessions: A list of XNAT project sessions
	:type project: str, optional
	:type commands: dict, optional
	:type scans: list, optional
	:type sessions: list, optional
	'''

	def __init__(self, xnat, project=None, commands={}, scans=[], sessions=[]):
		'''Constructor method
		'''

		self.xnat = xnat
		self.project = project
		self.commands = commands
		self.scans = []
		self.sessions = [] 
		self._has_experiments = False
		self._has_bids = False
		self._results = {}


	def set_commands(self, commands):
		'''Sets the commands for the command utility

		:param dict commands: Dictionary of commands with the XNAT project level 
			(i.e. project, session, or scan) as the keys and the command 
			name and options as the values.
		'''

		self.commands = commands

	def set_project(self, project):
		'''Sets the project name for the command utility

		:param str project: Name of the XNAT project
		'''

		self.project = project

	def find_project_experiments(self, project=None):
		'''Finds all of the sessions and scans under an XNAT project.

		:param project: The name of the XNAT project
		:type project: str, optional
		'''

		if project is not None: self.set_project(project)

		if self.project is None:
			raise ValueError('Unable to get project experiments: Project has not been defined.')

		self.scans = []
		self.sessions = []
		self._has_experiments = False
		try:
			uri = '/data/projects/{}/experiments'.format(self.project)
			res = self.xnat.get(uri).json()
			self.sessions.extend(res['ResultSet']['Result'])

			for exp in self.sessions:
				uri = '/data/experiments/{}/scans'.format(exp['ID'])
				res = self.xnat.get(uri).json()
				self.scans.extend([s for s in res['ResultSet']['Result'] if s['quality'] == 'usable'])
				self._has_experiments = True
		except Exception as ex:
			format_err(ex)

	def has_experiments(self, project=None):
		'''Determines if a project has experiments (sessions and/or scans)

		:param project: The name of an XNAT project
		:type project: str, optional
		:return: `True` if the XNAT project has sessions/scans, otherwise `False`
		:rtype: bool
		'''

		if project is not None: self.find_project_experiments(project)

		return self._has_experiments

	def get_project_experiments(self, project=None):
		'''Returns all of the sessions and scans in an XNAT project.

		:param project: The name of the XNAT project
		:type project: str, optional
		:return: Dictionary containing `sessions` and `scans` as keys 
			with the respective lists of each as values.
		:rtype: dict
		'''

		if project is not None: self.find_project_experiments(project)
		
		return {'sessions':self.sessions, 'scans':self.scans}

	def check_bids_map(self):
		'''Utility to check if a BIDS map exists within an XNAT project.
			If one does not exist, then one will be uploaded.
		'''

		if self.project is None:
			raise ValueError('Unable to check for BIDs map: Project has not been defined.')

		config_uri = '/data/projects/{}/config'.format(self.project)
		tools = []
		try:
			res = self.xnat.get(config_uri).json()
			tools.extend([i['tool'] for i in res['ResultSet']['Result']])
		except Exception as ex:
			format_err(ex)

		has_bids = True
		if 'bids' not in tools:
			logging.info('No BIDS map found in project {}. Uploading mapping now...'.format(self.project))
			try:
				with open('bmap.json','r') as f:
					bmap = json.load(f)
				tool_uri = '{}/bids/bidsmap?inbody=true'.format(config_uri)
				res = self.xnat.put(tool_uri, data=json.dumps(bmap,indent=2))
				res.raise_for_status()

				logging.info('Successfully uploaded BIDS map.')
			except Exception as ex:
				format_err(ex)
				has_bids = False 
		else:
			status_str = 'BIDS map found!'
			try:
				tool_uri = '{}/bids'.format(config_uri)
				res = self.xnat.get(tool_uri).json()
				for item in res['ResultSet']['Result']:
					if item['path'] == 'bidsmap':
						status_str += ' Status: {}, Created: {}'.format(item['status'],item['create_date'])
			except Exception as ex:
				format_err(ex)
			logging.info(status_str)

		self._has_bids = has_bids

	def get_wrapper_command(self,name,xsi):
		'''Function that looks for a function in an XNAT project matching a name and XSI type.

		:param str name: The name of the XNAT function
		:param str xsi: The domain level of the XNAT function (e.g. `xnat:mrScanData`)
		:return: XNAT function wrapper including the API endpoint to call the function
		:rtype: dict or None
		'''

		try:
			url = '/xapi/commands/available'
			opts = {'project':self.project,'xsiType':xsi}
			res = xnat.get(url,params=opts).json()

			for item in res:
				if not item['enabled']: continue
				if name not in item['command-name']: continue

				cmd = '/xapi/projects/{}/'.format(self.project)
				if 'wrapper-id' in item:
					cmd += 'wrappers/{}/launch'.format(item['wrapper-id'])
				elif 'command-id' in item and 'wrapper-name' in item:
					cmd += 'commands/{}/wrappers/{}/launch'.format(item['command-id'],item['wrapper-name'])
				else:
					continue

				item['launch'] = cmd 
				return item
		except Exception as ex:
			format_err(ex)
		return None

	def get_inputs(self, search_list):
		'''Recursively search an XNAT function wrapper for inputs.

		:param list search_list: List of XNAT functions 
		:return: XNAT function input information
		:rtype: dict
		'''

		defaults = {
			'static': None,
			'boolean': True,
			'text': ''
		}

		output = {}
		for item in search_list:
			try:
				if item['user-settable']:
					output[item['name']] = {'required':item['required'],'is_child':False,'default':''}
					if item['input-type'] in defaults: output[item['name']]['default'] = defaults[item['input-type']]
			except: pass
			
			try:
				c = get_inputs(item['children'])
				for k,v in c.items():
					v['is_child'] = True
					output[k] = v
			except: pass

		return output

	def get_container_info(self,url,params={}):
		'''Get XNAT container/plugin information and check that all required parameters are valid.

		:param params: Parameters passed to the XNAT container API
		:type params: dict, optional 
		:return: XNAT container information with valid input parameters
		:rtype: dict or None
		'''

		params['format'] = 'json'
		param_list = [params,params,params]
		for k,v in params.items():
			if '/data' in str(v):
				param_list[0][k] = param_list[0][k].replace('/data','/archive')
				v_split = param_list[2][k].split('/')
				if len(v_split) > 3:
					param_list[2][k] = '/'.join(v_split[3:])
				else:
					param_list[2][k] = v_split[-1]

		errs = []
		for opts in param_list:
			try:
				res = self.xnat.get(url,params=opts).json()
				inputs = self.get_inputs(res['input-config'])
				res['params'] = opts

				in_vals = res['input-values']

				errs = []
				for i in in_vals:
					try:
						name = i['name']
						if not i['values']:
							if inputs[name]['required'] and not inputs[name]['is_child']:
								errs.append('Required value "{}" missing from input values.'.format(name))
					except: pass

				if not errs: return res
			except Exception as ex:
				format_err(ex)

		for e in errs: logging.warning(e)
		return None

	def run_container(self,cmd,params):
		'''Run an XNAT container/plugin on a project, session, or scan.

		:param str cmd: XNAT command API endpoint to run command
		:param dict params: Parameters passed to the XNAT container API
		:return: Results of the command
		:rtype: dict
		'''

		result = {
			'command': cmd,
			'opts': params,
			'result': None,
			'error': False
		}
		try:
			if 'project' in params:
				output = self.xnat.post(cmd,
					headers={'Content-type': 'application/json'},
					data=json.dumps(params),
					timeout=None).json()
			else:
				output = self.xnat.post(cmd,
					headers={'Content-type': 'application/json'},
					data=json.dumps(params)).json()

			if 'status' in output:
				if output['status'] != 'success': 
					result['error'] = 'Status: {}'.format(output['status'])
					if 'message' in output: result['error'] += '. Message: {}'.format(output['message'])
			elif 'successes' in output:
				if 'failures' in output:
					if len(output['failures']) > 0:
						n_fail = len(output['failures'])
						n_total = n_fail + len(output['successes'])
						result['error'] = 'Warning: {}/{} containers failed to complete.'.format(n_fail,n_total)
			result['result'] = output
		except Exception as ex:
			format_err(ex)
			result['error'] = '{}'.format(ex)

		return result

	def find_and_run_command(self, exp_list, cmd, params={}):
		'''Function that runs a given XNAT command on a list of projects, sessions, of scans.

		:param list exp_list: A list of XNAT projects, sessions, or scans.
		:param str cmd: The name of the command 
		:param params: The optional parameters (or `kwargs`) that should be passed to the command
		:type params: dict, optional
		:return: List of the command results including the its wrapper and container information
		:rtype: list
		'''

		count = 0
		results = []
		try:
			for e in exp_list:
				count += 1
				logging.info('({}/{}) Gathering info on {}...'.format(count,len(exp_list),e['URI']))

				xsi = e['xsiType']
				xid = e['URI']

				logging.info('>> Getting wrapper...')
				wrapper = self.get_wrapper_command(cmd,xsi)
				if wrapper is None: 
					logging.warning('>> No command found for {} ({}).'.format(xid,xsi))
					continue

				root_elem = wrapper['root-element-name']
				opts = {k:v for k,v in params.items()}
				opts[root_elem] = xid
				
				logging.info('>> Getting container...')
				container = self.get_container_info(wrapper['launch'],opts)
				if container is None: 
					logging.warning('>> Unable to get container information for {} ({})'.format(xid,root_elem))
					continue

				logging.info('>> Running container...')
				result = self.run_container(wrapper['launch'],container['params'])
				
				if result is not None: logging.info('>> Success!')
				results.append({
					'info': e,
					'wrapper': wrapper,
					'container': container,
					'result': result
				})
		except Exception as ex:
			format_err(ex)

		return results

	def run_commands(self, project=None, commands=None):
		'''Run a series of commands on XNAT projects, sessions, or scans.

		:param project: Name of the XNAT project
		:param commands: Dictionary of commands with the XNAT project level 
			(i.e. project, session, or scan) as the keys and the command 
			name and options as the values.
		:type project: str, optional
		:type commands: dict, optional
		'''

		try:
			if project is not None: self.set_project(project)
			if commands is not None: self.set_commands(commands)

			if self.project is None: 
				raise ValueError('Unable to run commands: Project is not defined.')
			if not self.commands:
				raise ValueError('Unable to run commands: No commands found.')

			for level,cmd in commands.items():
				exp_list = []
				if level == 'scan':
					exp_list = self.scans 
				elif level == 'session':
					exp_list = self.sessions 
				elif level == 'project':
					exp_list = [{
						'xsiType': 'xnat:projectData',
						'URI': '/data/projects/{}'.format(self.project)
					}]
				else:
					logging.warning('Unexpected level found in commands: {}'.format(level))
					continue

				if 'bids' in cmd['name']:
					if not self._has_bids:
						self.check_bids_map()

				if exp_list:
					logging.info('Running "{}" on {} {}(s)'.format(cmd['name'],len(exp_list),level))
					self._results[k] = self.find_and_run_command(exp_list, cmd['name'], cmd['opts'])
				else:
					logging.info('Unable to run command "{}": No {}(s) found.'.format(cmd['name'],level))
		except Exception as ex:
			format_err(ex)

	def get_results(self):
		'''Returns the results stored in the command utility object

		:return: Results from running XNAT command(s)
		:rtype: dict
		'''

		return self._results



	def save_results(self, filename, indent=2):
		'''Save results from commands to a JSON file

		:param str filename: Name of the JSON file to save to 
			(`.json` extension not required)
		:param indent: The amount of spacing/indentation to 
			include while pretty-printing to output file
		:type indent: int, optional
		'''

		if not filename.endswith('.json'):
			filename = '{}.json'.format(filename)

		logging.info('Saving results to {}...'.format(filename))
		if self._results:
			write_json(self._results, filename, indent)
		else:
			logging.warning('Unable to write results to file: No results found.')

	def download_json_files(self, project=None, resource=''):
		'''Downloads data from JSON files located under an XNAT project 
		and (optionally) filtered by a resource name

		:param project: The name of the XNAT project
		:param resource: The name of the XNAT project resource
		:type project: str, optional
		:type resource: str, optional
		:return: A list of JSON structures downloaded from JSON files located
			in under a specific XNAT project/resource.
		:rtype: list
		'''

		if project is not None: self.set_project(project)
		if self.project is None: 
			raise ValueError('Unable to download project files: Project is not defined.')

		if resource != '': resource = 'resources/{}/'.format(resource)
		uri = '/data/projects/{}/{}files'.format(self.project,resource)

		logging.info('Searching for JSON files in {}'.format(uri))

		pct = 20
		output = []
		try:
			res = self.xnat.get(uri).json()
			res = [f['URI'] for f in res['ResultSet']['Result'] if f['URI'].endswith('json')]

			logging.info('Search complete. Downloading data from {} files...'.format(len(res)))
			for f in res:
				tmp = self.xnat.get(f).json()
				output.append(tmp)

				c_pct = 100*len(output)/len(res)
				if c_pct >= pct:
					logging.info('>> {}{} complete'.format(pct,'%'))
					pct += 20

			logging.info('>> Download complete!')
		except Exception as ex:
			format_err(ex)

		return output

if __name__ == '__main__': 
	pass
