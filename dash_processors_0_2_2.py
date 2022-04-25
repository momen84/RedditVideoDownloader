import json
import core
import requests
import xml.etree.ElementTree as ET

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent}

class Error(Exception):
	"""Base class for exceptions in this module."""
	pass

class NoneError(Error):
	"""Catch None values"""
	def __init__(self, expression, message):
		self.expression = expression
		self.message = message



def check_cross_post(json_script,identifier):
	try:
		identifier_2=json.loads(json_script).get('posts').get('models').get('t3_'+identifier).get('crosspostRootId').lstrip('t3_')
		if identifier!=identifier_2:
			return identifier_2
		else:
			return identifier
	except AttributeError:
		return identifier


def get_dashurl(json_script,identifier):
	
	identifier=check_cross_post(json_script,identifier)
	
	return 'Error','Error','Error'



def get_dash_file(dash_file_url):
	
	base_url='/'.join(dash_file_url.split('/')[:-1])+'/'
	dash_file=requests.get(dash_file_url,headers=headers)
	return dash_file_url,base_url,dash_file

def parse_video_dashUrl(dash_file,base_url):

	root = ET.fromstring(dash_file.text)
	
	files=[elem.text for elem in root.iter()]
	files_cleaned=[]
	for text in files:
		if text==None or ' ' in text:
			pass
		else:
			files_cleaned.append(base_url+text)
	
	download_files=core.thread_pool(len(files_cleaned),files_cleaned)
	
	return download_files

