import time
import json
import logging
from src.utils import (
	format_err,
	convert_seconds
)


class UIDImporter(object):
	'''Class that provides methods to import studies/scans to an XNAT 
	project using a list of study UIDs.

	:param class xnat: An open XNAT connection via pyxnat.Interface()
	:param str project: Name of the XNAT project
	:param uids: A list of study UIDs that will be imported
	:param filters: Dictionary with keys corresponding to the keyword 
		(e.g. `seriesDescription`) and values corresponding to a list 
		of approved values (e.g. [`Ax T1`,`Ax T2`]).
	:param studies: Dictionary with key values corresponding to study 
		UIDs and values corresponding to study descriptions.
	:type uids: str or list, optional
	:type filters: dict, optional
	:type studies: dict, optional
	'''

	def __init__(self, xnat, project, uids=[], filters={}, studies={}):
		'''Constructor method
		'''

		self.xnat = xnat
		self.project = project
		self.studies = studies
		self.set_uids(uids)
		self.set_filters(filters)
		self.set_scp_params()

	def set_project(self, project):
		'''Sets the project name for the UID importer

		:param str project: Name of the XNAT project
		'''

		self.project = project

	def set_uids(self,uids=[]):
		'''Sets the UIDs that the import tool will 
		look for and download (if found).

		:param uids: Single or list of study UIDs
		:type uids: list or str, optional
		'''

		self.uids = []
		if uids:
			if isinstance(uids,list):
				self.uids = [str(i) for i in uids]
			else:
				self.uids.append(uids)

	def set_filters(self,filt={}):
		'''Sets the filters that will be used to filter the list of studies 
		imported into a project.

		:param filt: Dictionary with keys corresponding to the keyword 
			(e.g. `seriesDescription`) and values corresponding to a list 
			of approved values (e.g. [`Ax T1`,`Ax T2`]).
		:type filt: dict, optional
		'''

		self.filters = filt

	def set_scp_params(self, project=None):
		'''Sets the parameters for the XNAT DICOM/SCP connection.

		:param project: Name of the XNAT project to use
		:type project: str, optional
		'''

		self.scp = None
		if project is None: project = self.project

		logging.info('Gathering SCP parameters...')
		try:
			info = self.xnat.get('/xapi/dicomscp').json()[0]
			scp_info = {
				'pacsId': info['id'],
				'ae': '{}%3A{}'.format(info['aeTitle'],info['port']),
				'project': project
			}
			logging.info('...success!')
			logging.debug('SCP Info:\n{}'.format(json.dumps(scp_info,indent=2)))
			self.scp = scp_info
		except Exception as ex:
			format_err(ex)

	def find_studies(self, uids=[]):
		'''Find studies using a list of study UIDs

		:param uids: List of study UIDs
		:type uids: list, optional
		'''

		self.studies = {}
		if uids: self.set_uids(uids)

		if not self.uids:
			logging.warning('Unable to get studies: No UIDs found.')
			return

		data_str = ','.join(self.uids)
		logging.info('Gathering studies for UID(s): {}'.format(data_str))
		try:
			'''
			Send data to the API, which will return an unflitered list of studies
			'''
			res = self.xnat.post('/xapi/dqr/seriesInfo/pacs/1/studies', 
				data=data_str).json()
			res.raise_for_status()
			
			'''
			Loop through list of studies and filter out unwanted ones. Any
			reminaing study information will be added to the "studies" structure
			'''
			studies = {}
			for uid in self.uids:
				try:
					tmp = res[uid]
					filtered_list = []
					for item in tmp['results']:
						add_item = True
						if self.filters:
							for k,v in self.filters.items():
								if item[k] not in v: add_item = False
						if add_item: filtered_list.append(item)
					if len(filtered_list) > 0: 
						studies[uid] = {
							"seriesDescriptions": list(set([i['seriesDescription'] for i in filtered_list])),
							"seriesInstanceUids": list(set([i['seriesInstanceUid'] for i in filtered_list])),
						}
				except Exception as ex:
					format_err(ex)

			logging.info('Search complete: {} Studies found.'.format(len(studies)))
			self.studies = studies
		except Exception as ex:
			format_err(ex)

	def get_studies(self):
		'''Get the list of currently loaded studies

		:return: Dictionary with key values corresponding to study UIDs
		:rtype: dict
		'''

		return self.studies

	def import_studies(self, studies=None):
		'''Imports a list of studies into an XNAT project

		:param studies: Dictionary with key values corresponding to study UIDs
		:type studies: dict, optional
		:return: `True` if request was successful, `False` otherwise
		:rtype: bool
		'''

		try:
			if self.scp is None: 
				logging.warning('Unable to import studies: No dicomscp parameters found.')
				return False

			if studies is not None: self.studies = studies
			if not self.studies:
				logging.warning('Unable to import studies: No studies found.')
				return False

			logging.info('Importing data from PACS...')
			logging.debug('Data:\n{}'.format(json.dumps(self.studies,indent=2)))

			url = '/xapi/dqr/csvimport/generalImportFromJson?'
			url += '&'.join(['{}={}'.format(k,v) for k,v in self.scp.items()])

			logging.debug('Post URL: http://172.30.205.46{}'.format(url))

			res = self.xnat.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
			res.raise_for_status()
			logging.info('...success! Subject(s) were successfully added to {}.'.format(self.scp['project']))

			return True
		except Exception as ex:
			format_err(ex)
		return False

	def check_import_queue(self, project=None):
		'''Checks the XNAT import queue for all items related to the project

		:param project: The name of the project which will be used to filter the studies
		:type project: str, optional
		:return: Dictionary containing the total number of sessions, total number of scans, and a list of all sessions
		:rtype: dict
		'''

		if project is None: project = self.project

		output = {
			'total_sessions': 0,
			'total_scans': 0,
			'sessions': []
		}
		try:
			res = self.xnat.get('/xapi/dqr/query/queue/all?format=json').json()
			for item in res:
				if item['xnatProject'] == project:
					n_series = len(item['seriesIds'].split(','))
					output['total_sessions'] += 1
					output['total_scans'] += n_series
					q_time = item['timestamp']/1000 - item['queuedTime']/1000
					output['sessions'].append({
						'status': item['status'],
						'num_scans': n_series,
						'studyUID': item['studyInstanceUid'],
						'sec_queued': q_time
					})
		except Exception as ex:
			format_err(ex)

		return output

	def monitor_import_queue(self, timeout=180, time_refresh=True):
		'''Monitors the status of studies that are being imported to a project.

		:param timeout: The amount of time (in seconds) to monitor the queue, defaults to 180
		:param time_refresh: Tells the monitor whether or not to restart the timeout if there is a status change, defaults to True
		:type timeout: int, optional
		:type time_refresh: bool, optional
		'''

		s_time = time.time()

		has_populated = False
		while True:
			q_data = self.check_import_queue()

			t_elapsed = time.time() - s_time

			if q_data['total_sessions'] > 0:
				has_populated = True
				n_sess = q_data['total_sessions']
				n_scan = q_data['total_scans']
				status_str = '{} sessions containing {} scans are currently queued.'.format(n_sess,n_scan)
				q_statuses = {}
				for item in q_data['sessions']:
					tmp = item['studyUID'].split('.')
					short_uid = '{}...{}'.format('.'.join(tmp[:3]),'.'.join(tmp[-2:]))
					t_q = convert_seconds(item['sec_queued'])
					status_str += '\n\t>> {} ({} queue time): '.format(short_uid,t_q)
					status_str += '{} scans are {}'.format(item['num_scans'],item['status'])

				if t_elapsed > timeout:
					status_str += 'There are items still in the queue, but is taking longer than usual to finish. '
					status_str += 'Try manually monitoring these items in the browser. Exiting queue monitor.'
			else:
				if has_populated:
					status_str = 'There are no more items in the queue. Exiting queue monitor.'
				else:
					if t_elapsed < 60:
						status_str = 'Waiting for items to arrive in queue...'
					else:
						status_str = 'Time limit exceeded and no items were found. Exiting queue monitor.'

			if status_str != old_status:
				logging.info('Queue Updated:\n{}'.format(status_str))
				old_status = status_str
				if time_refresh: s_time = time.time()

			if 'Exiting queue monitor.' in status_str: return
			time.sleep(1)

if __name__ == '__main__': 
	pass
	