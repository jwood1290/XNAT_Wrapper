import logging

'''
Initialize logging level and format
'''
logging.basicConfig(level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

'''
XNAT connection variables
s'''
xnat_ip = 'your.xnat.ip.address'
xnat_username = 'xnat_username'
xnat_password = 'xnat_password'
xnat_project = 'xnat_example_project'

'''
Filenames to store results in
'''
results_file = 'example_mriqc.json'
results_csv = 'example_mriqc.csv'

'''
List of study UIDs that you want to import
'''
uid_list = [
	'study.UID.number.1',
	'study.UID.number.2'
]

'''
List of filters that we will use to only pull files that are relevant 
to what we are trying to do (in this case, only DICOM files with 
series descriptions of "Ax T1" and "Ax T2")
'''
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