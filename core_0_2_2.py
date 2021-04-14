#! /usr/bin/python3
import json
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import sys
from requests.sessions import session
# import dash_processors
# import dash_processors_0_2_1 as dash_processors

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

class ExternalSource(Error):
	"""Catch External redirects"""
	def __init__(self, expression, message):
		self.expression = expression
		self.message = message



class RedPost():
	def __init__(self,json_script):
		self.json_script = json_script
		# print(self.json_script)
		self.post_id=[x for x in json.loads(self.json_script).get('posts').get('models').keys()][0]
		self.cross_post=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('crosspostParentId')
		# self.post_id=self.checkCrossPost()
		# print(self.post_id)
		self.post_attrs=[x for x in json.loads(json_script).get('posts').get('models').get(self.post_id).items()]
		
		self.removed_flag=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('removedByCategory')
		
		self.mediaDomain()
		if self.removed_flag=="deleted" and 'redd.it' in self.mediadomain:
			print('Post was hosted in Reddit but now deleted , cannot proceed')
			return None
		self.post_title=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('title')
		self.getThumbnail()
		self.NSFWFlag()
		
		# print(self.mediadomain)
		if self.mediadomain=='v.redd.it':
			self.getRedditMediaUrls()
		else:
			if self.mediadomain =='youtu.be':
				self.getYoutube()
			else:
				self.getExternalMediaUrls()
		
		# print(f'Post Attributes={self.post_attrs}')
		
		# print(f'Post ID ={self.post_id}')
		# print(f'Title ={self.post_title}')
		# print(f'Removed flag={self.removed_flag}')
		# print(f'Cross post to ={self.cross_post}')
		# print(f'Thumbnail URL ={self.thumbnail}')
		# print(f'NSFW Flag ={self.NSFW}')
		# print(f'Media Type ={self.media_type}')
		# print(f'Media URLs ={self.media_urls}')
		# print(f'Media domain ={self.mediadomain}')

		# print('Post ID ={}'.format(self.post_id))
		# print('Title ={}'.format(self.post_title))
		# print('Removed flag={}'.format(self.removed_flag))
		# print('Cross post to ={}'.format(self.cross_post))
		# print('Thumbnail URL ={}'.format(self.thumbnail))
		# print('NSFW Flag ={}'.format(self.NSFW))
		# print('Media Type ={}'.format(self.media_type))
		# print('Media URLs ={}'.format(self.media_urls))
		# print('Media domain ={}'.format(self.mediadomain))

		# print(f'Source={source}')

	def checkCrossPost(self):
		if self.cross_post==self.post_id:
			self.post_id=self.post_id	# else:
		# 	print(f'Post hase been removed by : {self.removed_flag} , however we will try to download any ways')
		# 	self.thumbnail = None

		
	def getThumbnail(self):
		# self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('thumbnail').get('url')
		if self.removed_flag==None:
			try:
				self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('thumbnail').get('url')
			
			except AttributeError:
				# self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get(self.cross_post).get('thumbnail').get('url')
				self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.cross_post).get('thumbnail').get('url')
			
			finally :
				try:
					self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('preview').get('url')
				except:
					# self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get(self.cross_post).get('preview').get('url')
					self.thumbnail=json.loads(self.json_script).get('posts').get('models').get(self.cross_post).get('preview').get('url')
		else:
			# print(f'Post hase been removed by : {self.removed_flag} , however we will try to download any ways')
			print('Post hase been removed by : {} , however we will try to download any ways'.format(self.removed_flag))
			self.thumbnail = None

	def mediaDomain(self):
		self.mediadomain=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('domain')

	def getRedditMediaUrls(self):
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
			
			self.download_files=thread_pool(len(files_cleaned),files_cleaned)
			
			# return download_files


		try:
			self.media_type=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('media').get('type')
			self.media_urls=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('media').get('dashUrl')
			dash_file_url,base_url,dash_file=get_dash_file(self.media_urls)
			parse_video_dashUrl(dash_file,base_url)
			
		
		except AttributeError:
			self.media_type=json.loads(self.json_script).get('posts').get('models').get(self.cross_post).get('media').get('type')
			self.media_urls=json.loads(self.json_script).get('posts').get('models').get(self.cross_post).get('media').get('dashUrl')
			dash_file_url,base_url,dash_file=get_dash_file(self.media_urls)
			parse_video_dashUrl(dash_file,base_url)

	

		
	
	
	def NSFWFlag(self):
		try:
			self.NSFW=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('isNSFW')
		except:
			self.NSFW=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get(self.cross_post).get('isNSFW')
	
	def getExternalMediaUrls(self):
		def process_external_json_redgifs(json_text):
			self.thumbnail=json.loads(json_text).get('image').get('thumbnailUrl')
		def process(r):
			download_files=[]
			bsobj=BeautifulSoup(r.text,'lxml')
			videos=bsobj.find('video')
			try:
				json_text=bsobj.find('script',{'type':"application/ld+json"}).string
				process_external_json_redgifs(json_text)	
			except AttributeError:
				pass
			for source in videos.findAll('source'):
				download_file_={}
				file_url=source.attrs['src']
				r.close()
				download_files.append(file_url)
				
			self.download_files=thread_pool(len(download_files),download_files)	
		
		def process_imgur(url):
			print(url)
		try:
			self.media_urls=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('source').get('url')
			self.media_type='External Content'
		except AttributeError:
			self.media_urls=json.loads(self.json_script).get('posts').get('models').get(self.cross_post).get('source').get('url')
			self.media_type='External Content'
		media_checker=self.media_urls.split('.')[-1]
		if 'imgur' in self.media_urls or media_checker in ['mp4','gif','gifv']:
			self.media_urls=self.media_urls.replace(media_checker,'mp4')
			self.download_files=get_size(self.media_urls)
		
		else:
			try:
				r=requests.get(self.media_urls,headers=headers)
				if r.status_code==200:
					
					process(r)
			except ConnectionError:
				print('Connection Error raised ,Proxify')
				session=proxify()
				r=session.get(self.media_urls,headers=headers)
				process(r)
			except requests.exceptions.SSLError:
				print('SSLERROR raised , Proxify')
				session=proxify()
				r=session.get(self.media_urls,headers=headers)
				process(r)

	def getYoutube(self):
		self.media_type=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('media').get('provider')
		self.media_urls=json.loads(self.json_script).get('posts').get('models').get(self.post_id).get('source').get('url')
		self.download_files=None
		
		


def sizeof_fmt(num, suffix='B'):
	for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, 'Yi', suffix)

def proxify():
	session = requests.session()
	session.proxies['http'] = 'socks5h://localhost:9050'
	session.proxies['https'] = 'socks5h://localhost:9050'
	return session	
		



def get_size(file_url):	
	download_file={}
	try:
		r=requests.get(file_url,headers=headers)
		download_file['URL']=file_url
		download_file['Size']=sizeof_fmt(int(r.headers['content-length']))
		# download_file['Thumbnail']=
		return download_file
	
	except ConnectionError:
		session = proxify()
		r=session.get(file_url,headers=headers)
		download_file['URL']=file_url
		download_file['Size']=sizeof_fmt(int(r.headers['content-length']))
		# download_file['Thumbnail']=
		return download_file
	except requests.exceptions.SSLError:
		session = proxify()
		r=session.get(file_url,headers=headers)
		download_file['URL']=file_url
		download_file['Size']=sizeof_fmt(int(r.headers['content-length']))
		# download_file['Thumbnail']=
		return download_file
	



def thread_pool(len_files_cleaned,files_cleaned):
	import concurrent.futures
	with concurrent.futures.ThreadPoolExecutor(max_workers=len(files_cleaned)) as executor:
		future = executor.map(get_size,files_cleaned)
		download_files=[x for x in future]
	return download_files




def get_outsiders(url):
	files_cleaned=[]
	try:
		r=requests.get(url,headers=headers)
		if r.status_code==200:
			bsobj=BeautifulSoup(r.text,'lxml')
			videos=bsobj.find('video')
			
			for source in videos.findAll('source'):
				files_cleaned.append(source.attrs['src'])
	except ConnectionError:
		session = proxify()
		r=session.get(url,headers=headers)
		if r.status_code==200:
			bsobj=BeautifulSoup(r.text,'lxml')
			videos=bsobj.find('video')
			
			for source in videos.findAll('source'):
				files_cleaned.append(source.attrs['src'])
	download_files=thread_pool(len(files_cleaned))
	return download_files
	
	

def select_file(download_files):
	for index,file in enumerate(download_files):
		print('{} - {}'.format(index, file))
	file_selection=int(input('Please enter file selection: '))
	selected_file=download_files[file_selection]
	return selected_file


def download(file_url):
	identifier=file_url.split('/')[3]
	quality=file_url.split('/')[-1]
	
	file_name=identifier+'_'+quality
	if file_name.endswith('.mp4'):
		file_name=file_name
	else:
		file_name=file_name+'.mp4'
	
	with open(file_name,'wb') as downloaded:
		session=proxify()
		r=session.get(file_url,headers=headers,stream=True)
		for data in r.iter_content(1024):
			downloaded.write(data)

def req_url(url):
	# print('req_url {}'.format(url))
	identifier=url.split('/')[6]
	r=requests.get(url,headers=headers)
	if r.status_code==200:
		bsobj=BeautifulSoup(r.text,'lxml')
		script=bsobj.find('script',{'id':'data'})

		json_script=json.loads(script.string.strip().replace('window.___r = ','').rstrip(';'))
		json_formated=json.dumps(json_script,indent=4)

		return r.status_code,url,identifier,json_formated


def starterStandAlone(url):
	status,url,identifier,json_formated=req_url(url)
	dash_file_url,base_url,dash_file=dash_processors.get_dashurl(json_formated,identifier)

	if dash_file is None:
		print('File links to conent outside reddit')
		# file_url=dash_file_url
		download_files=dash_file_url
		# print(download_files)
		selected_file=select_file(download_files)
		download(selected_file['URL'])
		
	else:
		download_files=dash_processors.parse_video_dashUrl(dash_file,base_url)
		if len(download_files)==1:
			print(download_files)
			selected_file=download_files[0]
			print('Downloadong {}'.format(selected_file))
			download(download_files[0]['URL'])
			
		else:
			print(download_files)
			selected_file=select_file(download_files)
			print('Downloadong {}'.format(selected_file))			
			download(selected_file['URL'])
			
	

def starterApi(url):
	status,url,identifier,json_formated=req_url(url)
	# dash_file_url,base_url,dash_file=dash_processors.get_dashurl(json_formated,identifier)

	post=RedPost(json_formated)
	try:
		# return post.post_id,post.post_title,post.removed_flag,post.cross_post,post.thumbnail,post.NSFW,post.media_type,post.media_urls,post.mediadomain,post.download_files
		return {"links":post.download_files,"thumbnail":post.thumbnail}
	except:
		return 'Error ..... Post was hosted in Reddit but now deleted , cannot proceed'


	# if dash_file is None:
	# 	print('File links to conent outside reddit')
	# 	download_files=dash_file_url

	# elif dash_file=='Error':
	# 	download_files='Error'
		
	# else:
	# 	download_files=dash_processors.parse_video_dashUrl(dash_file,base_url)
	# 	if len(download_files)==1:
	# 		selected_file=download_files[0]
			
	# return download_files			


