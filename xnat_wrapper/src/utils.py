import sys
import json
import time
import logging
import traceback

def format_err(err_str=None):
	'''Formats and prints Exceptions and error messages

	:param err_str: The error message to be formatted and logged
	:type err_str: str or Exception, optional
	'''

	try:
		tb = sys.exc_info()[2]
		exc_tb = traceback.extract_tb(tb)[-1]
		fname = exc_tb[0].split('site-packages/')[-1]
		line = exc_tb[1]
		func = exc_tb[2]
		if err_str is None: err_str = exc_tb[3]
		err_msg = '({}, {}, line {}): {}'.format(fname,func,line,err_str)
	except Exception as ex:
		if err_str is None:
			err_msg = 'There was an error trying to parse the original error: {}'.format(ex)
		else:
			err_msg = '{}'.format(err_str)
	logging.error(err_msg)

def convert_seconds(s,fmt=None):
	'''Converts seconds to hours, minutes, and seconds (or
	whatever format is specified)

	:param float s: Amount of seconds to convert to hours, minutes, and seconds
	:param fmt: Formatting string for output (e.g. "%i minutes and %i seconds")
	:type fmt: str, optional
	:return: Formatted time string
	:rtype: str
	'''
	
	if isinstance(s, str):
		try:
			s = float(s)
		except:
			try:
				s = int(s)
			except:
				s = 0
		
	m,s = divmod(s,60)
	h,m = divmod(m,60)
	
	h = int(h)
	m = int(m)

	h_str = '{} {}'.format(h,'hour' if h == 1 else 'hours')
	m_str = '{} {}'.format(m,'minute' if m == 1 else 'minutes')
	s_str = '{:.2f} {}'.format(s,'second' if s == 1 else 'seconds')

	output = None
	if fmt is not None:
		try:
			nargs = max(fmt.count('{'), fmt.count('%'))
			if nargs == 3:
				output = fmt.format(h,m,s)
			elif nargs == 2:
				m += h*60
				output = fmt.format(m,s)
			elif nargs == 1:
				s += (h*60 + m*60)
				output = fmt.format(s)
		except: pass

	if output is None:
		if h > 0:
			output = '{}, {}, and {}'.format(h_str,m_str,s_str)
		elif m > 0:
			output = '{} and {}'.format(m_str,s_str)
		elif s < 0.01:
			output = '{:.2f} ms'.format(s*1000)
		else:
			output = s_str

	return output

def write_json(data, fname, indent=2):
	'''Pretty-prints a JSON/dictionary object to file

	:param dict data: JSON/dictionary object to be written to file
	:param str fname: Output filename for JSON file
	:param indent: Amount of file spacing/indentation for pretty-printing, defaults to 2
	:type indent: int, optional
	'''

	if not fname.endswith('.json'): fname += '.json'

	try:
		with open(fname,'w') as f:
			f.write(json.dumps(data,indent=indent))
	except Exception as ex:
		format_err(ex)

def json_to_csv(files,fname,keys=[]):
	'''Converts a list of JSON/dict structures to a list of 
	comma separated values (CSV) and saves it to a file.

	:param list files: A list of JSON/dict structures
	:param str fname: The name of the CSV file that will be written to
	:param keys: A list of CSV column headers that should be added 
		to the file, which are not already base key/value 
		pairs in the JSON/dict structures
	:type keys: list, optional
	'''

	if not fname.endswith('.csv'): fname += '.csv'

	headers = []
	with open(fname,'w') as csv:
		for f in files:
			if len(headers) == 0:
				headers.extend(keys)
				headers.extend([k for k,v in f.items() if not isinstance(v,dict)])
				line = ','.join(headers)
				csv.write('{}\n'.format(','.join(headers)))

			output = {h:'' for h in headers}
			for key,value in f.items():
				if key in output:
					output[key] = str(value)
				else:
					for k in keys:
						if k in value: output[k] = str(value[k])

			csv.write('{}\n'.format(','.join([v.replace(',',';') for k,v in output.items()])))

def parse_csv(fname,filt=[]):
	'''Converts a CSV file into a dictionary structure containing all columns 
	unless specific columns are defined using the `filt` parameter.

	:param str fname: Name of CSV file (with or without extension)
	:param filt: List of column headers (whole or partial) to keep
	:type filt: list, optional
	:return: Dictionary with CSV column headers as keys and columns as values
	:rtype: dict
	'''

	count = 0
	output = {}
	if not fname.endswith('.csv'): fname += '.csv'
	with open(fname,'r') as f:
		for line in f:
			count += 1
			line = line.replace('\n','')
			if count == 1:
				columns = [h.replace(' ','') for h in line.split(',')]
			else:
				items = line.split(',')
				if len(items) != len(columns):
					print('Line {} has incorrect amount of inputs: {} != {}'.format(count,len(items),len(columns)))
					continue

				for col,val in zip(columns,items):
					try:
						val = float(val)
					except: pass

					try:
						output[col].append(val)
					except:
						output[col] = [val]

	blacklist = []
	for k,v in output.items():
		if any(isinstance(val,str) for val in v):
			if k.lower() not in [f.lower() for f in filt]: blacklist.append(k)

	return {k.lower():v for k,v in output.items() if k not in blacklist}

if __name__ == '__main__': 
	pass