import logging

logging.basicConfig(level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

login_file = 'xnat_login.cfg'
results_file = 'upload_test_mriqc.json'
results_csv = 'mriqc_results.csv'

project = 'upload_test'

uid_list = [
	'study.UID.number.1',
	'study.UID.number.2'
]

filters = {
	'seriesDescription': [
		"Ax T1",
		"Ax T2"
	]
}

'''
Define the commands that will be run on projects, sessions, and/or scans
'''
commands = {
	'scan': {
		'name': 'dcm2niix',
		'opts': {'bids':True}
	},
	'session': {
		'name': 'dcm2bids-session',
		'opts': {'overwrite':True}
	},
	'project': {
		'name': 'bids-mriqc',
		'opts': {'flags':''}
	}
}

'''
Define the resource folder in which to look for the appropriate JSON files.
'''
resource_dir = 'MRIQC'

'''
Include additional headers in CSV that are not base key/value pairs
in the json structures (files) returned from XNAT
'''
add_keys = ['subject_id','session_id','modality']