#!/usr/bin/env python

CONNECT_TIMEOUT = 30
GET_TIMEOUT = 60
TRIES = 30

import sys, os, ftplib, ConfigParser, MySQLdb, cStringIO, pycurl, re, datetime, time, urllib, threading, socket, random
import hashlib

class rePixer:
	def __init__(self, sqlConfig, siteFtpConfig, imageHostersConfig):
		host = sqlConfig.get("MySQL", "host")
		user = sqlConfig.get("MySQL", "user")
		password = sqlConfig.get("MySQL", "password")
		db = sqlConfig.get("MySQL", "db")
		self.mysqlConnect = MySQLdb.connect(host, user, password, db)
		self.mysqlCursor = self.mysqlConnect.cursor()
		self.mysqlCursor.execute("SELECT `id`, `screenlist` FROM `f3x_posts` WHERE `repix` = 0 ORDER BY `id` DESC LIMIT 0, 3000")
		self.mysqlConnect.commit()
		self.slList = dict()
		for data in self.mysqlCursor.fetchall():
			self.slList[data[0]] = data[1].split("|")

		self.siteFtpConfig = siteFtpConfig
		self.imageHostersConfig = imageHostersConfig
		self.lock = threading.Lock()
		return

	def repixMe(self):
		if not os.path.exists('/tmp/repixer'):
			os.mkdir('/tmp/repixer')
		os.chdir('/tmp/repixer')
		print "Starting repixing..."
		for slData in self.slList.items():
			print "Current post: {0}".format(slData[0],)
			slLinks = list()
			for sl in slData[1]:
				processList = list()
				print "Processing screenlist: {0}...".format(sl[2:],)
				screenList = self.getFileFromFTP("Free3x", sl[2:])
				size = os.path.getsize(screenList)
				if size < 1024000:
					process = threading.Thread(target = self.iPictureCallback, args = (screenList, slLinks))
					process.name = "iPictureCallback"
					process.daemon = False
					#processList.append(process)
					process = threading.Thread(target = self.PicSeeCallback, args = (screenList, slLinks))
					process.name = "PicSeeCallback"
					process.daemon = False
					processList.append(process)
					process = threading.Thread(target = self.ImageVenueCallback, args = (screenList, slLinks))
					process.name = "ImageVenueCallback"
					process.daemon = False
					processList.append(process)
					process = threading.Thread(target = self.Image2YouCallback, args = (screenList, slLinks))
					process.name = "Image2YouCallback"
					process.daemon = False
					processList.append(process)
					process = threading.Thread(target = self.Pic4YouCallback, args = (screenList, slLinks))
					process.name = "Pic4YouCallback"
					process.daemon = False
					processList.append(process)
					process = threading.Thread(target = self.Pic4PayCallback, args = (screenList, slLinks))
					process.name = "Pic4PayCallback"
					process.daemon = False
					processList.append(process)
					process = threading.Thread(target = self.PicCashCallback, args = (screenList, slLinks))
					process.name = "PicCashCallback"
					process.daemon = False
					#processList.append(process)
					process = threading.Thread(target = self.PlatimZaFotoCallback, args = (screenList, slLinks))
					process.name = "PlatimZaFotoCallback"
					process.daemon = False
					#processList.append(process)
					for process in processList:
						process.start()
					for process in processList:
						while process.isAlive():
							time.sleep(1)
					print "Processing screenlist: {0}...Done".format(sl[2:],)
			if len(slLinks) > 4:
				slLinks = '|'.join(slLinks)
				print "Updating db..."
				sql = "UPDATE `f3x_posts` SET `repix` = 1, `screenlist` = '{0}' WHERE `id` = {1}".format(slLinks, slData[0])
				self.mysqlCursor.execute(sql)
				self.mysqlConnect.commit()
				print "Updating db...Done"
				print "Caching post http://free-3x.com/#post-{0}...".format(slData[0],)
				self.get("http://free-3x.com/showPost/{0}/ajax".format(slData[0],))
				print "Caching post http://free-3x.com/#post-{0}...Done".format(slData[0],)
				self.delFileFromFTP("Free3x", sl[2:])
			print "\n"
		print "Starting repixing...Done"
		return

	def delFileFromFTP(self, ftpData, filePath):
		print "Deleting file {0}...".format(filePath,)
		for tries in range(0, 30):
			print "Connecting to host: {0}...".format(self.siteFtpConfig.get(ftpData, "host"),)
			ftp = ftplib.FTP()
			try:
				ftp.connect(self.siteFtpConfig.get(ftpData, 'host'))
				ftp.login(self.siteFtpConfig.get(ftpData, 'user'), self.siteFtpConfig.get(ftpData, 'password'))
				ftp.cwd(self.siteFtpConfig.get(ftpData, 'folder'))
				ftp.delete("{0}".format(filePath,))
				ftp.close()
				break
			except:
				ftp.close()
				print "Error: {0}\nTry: {1}".format(sys.exc_info(), tries)
				continue
		print "Deleting file {0}...Done".format(filePath,)
		return self

	def getFileFromFTP(self, ftpData, filePath):
		print "Getting file {0}...".format(filePath,)
		for tries in range(0, 30):
			print "Connecting to host: {0}...".format(self.siteFtpConfig.get(ftpData, "host"),)
			ftp = ftplib.FTP()
			try:
				ftp.connect(self.siteFtpConfig.get(ftpData, 'host'))
				ftp.login(self.siteFtpConfig.get(ftpData, 'user'), self.siteFtpConfig.get(ftpData, 'password'))
				ftp.cwd(self.siteFtpConfig.get(ftpData, 'folder'))
				try:
					ftp.retrbinary("RETR {0}".format(filePath,), open(os.path.basename(filePath), 'wb').write)
					ftp.close()
					break
				except:
					ftp.close()
					print "File not found on FTP"
					return
				break
			except:
				ftp.close()
				print "Error: {0}\nTry: {1}".format(sys.exc_info(), tries)
				continue
		print "Getting file {0}...Done".format(filePath,)
		return os.path.basename(filePath)

	def ImageVenueCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "ImageVenueCallback: processing {0}...".format(pic,)
			self.lock.release()
			curl = pycurl.Curl()
			srvc = 'ImageVenue.com'
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic))]
			for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
				postData.append(tuple(item for item in equals.split('=')))
			try:
				page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
				link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), page).group(1)
				self.lock.acquire()
				print "ImageVenueCallback: {0}".format(link)
				slLinks.append(link)
				self.lock.release()
				return
			except:
				print "ImageVenueCallback: Error in Link\nImageVenueCallback: try {0}".format(tries)
				continue
		return

	def iPictureCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "iPictureCallback: processing {0}...".format(pic,)
			self.lock.release()
			curl = pycurl.Curl()
			srvc = 'iPicture.ru'
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic))]
			for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
				postData.append(tuple(item for item in equals.split('=')))
			try:
				page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, cookies=True)
				refreshUrl = re.search(self.imageHostersConfig.get(srvc, 'refreshUrlRx'), page).group(1)
				page = self.get(refreshUrl)
				try:
					link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), page).group(1)
					self.lock.acquire()
					print "iPictureCallback: {0}".format(link)
					slLinks.append(link)
					self.lock.release()
					return
				except:
					print "iPictureCallback: Error in Link\nTry: {0}".format(tries)
					continue
			except:
				print "iPictureCallback: Error in refreshUrl\niPictureCallback: try {0}".format(tries)
				continue
		return

	def PicSeeCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "PicSeeCallback: processing {0}...".format(pic,)
			curl = pycurl.Curl()
			srvc = 'PicSee.net'
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic))]
			print "PicSeeCallback: Using proxy..."
			self.lock.release()
			try:
				proxy = False
				if socket.gethostname() == 'vps2':
					proxy = True
				page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, proxy)
				link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), page).group(1)
				self.lock.acquire()
				print "PicSeeCallback: {0}".format(link)
				slLinks.append(link)
				self.lock.release()
				return
			except:
				print "PicSeeCallback: Error in refreshUrl\nPicSeeCallback: try {0}".format(tries)
				continue
		return

	def Image2YouCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "Image2YouCallback: processing {0}...".format(pic,)
			self.lock.release()
			curl = pycurl.Curl()
			srvc = 'Image2You.ru'
			self.get(self.imageHostersConfig.get(srvc, 'getUrl'), cookies=True)
			self.get(self.imageHostersConfig.get(srvc, 'authUrl'), cookies=True)
			self.get(self.imageHostersConfig.get(srvc, 'getUrl'), cookies=True)
			page = self.get(self.imageHostersConfig.get(srvc, 'getUrl2'), cookies=True)
			try:
				session = re.search("'session': '(.+)'", page).group(1)
				postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic))]
				for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
					equals = re.sub('\{pic\}', pic, equals)
					equals = re.sub('\{session\}', session, equals)
					postData.append(tuple(item for item in equals.split('=')))
				self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, cookies=True)
				page = self.get(self.imageHostersConfig.get(srvc, 'getUrlWithPic'), cookies=True)
				link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), page).group(1)
				self.lock.acquire()
				print "Image2YouCallback: {0}".format(link)
				slLinks.append(link)
				self.lock.release()
				return
			except:
				print "Image2YouCallback: Error in session\nImage2YouCallback: try {0}".format(tries)
				continue
		return

	def Pic4YouCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "Pic4YouCallback: processing {0}...".format(pic,)
			self.lock.release()
			curl = pycurl.Curl()
			srvc = 'Pic4You.ru'
			try:
				page = self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'), cookies=True)
			except:
				print "Pic4YouCallback: Error in auth\nPic4YouCallback try {0}".format(tries)
				continue
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic))]
			for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
				postData.append(tuple(item for item in equals.split('=')))
			try:
				page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, cookies=True).decode('cp1251')
			except:
				print "Pic4YouCallback: Error in postFile\nPic4YouCallback try {0}".format(tries)
				continue
			try:
				link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), page).group(1)
				self.lock.acquire()
				print "Pic4YouCallback: {0}".format(link)
				slLinks.append(link)
				self.lock.release()
				return
				break
			except:
				print "Pic4YouCallback: Error in link\nPic4YouCallback try {0}".format(tries)
				continue
		return

	def Pic4PayCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "Pic4PayCallback: processing {0}...".format(pic,)
			self.lock.release()
			curl = pycurl.Curl()
			srvc = 'Pic4Pay.com'
			page = self.get(self.imageHostersConfig.get(srvc, 'authUrl'), cookies=True)
			if not re.search('Location: /', page):
				self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'), cookies=True)
			page = self.get(self.imageHostersConfig.get(srvc, 'getUrl'), cookies=True)
			session = re.search("'PHPSESSID':'(\w+)'", page).group(1)
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic)), ('PHPSESSID', session)]
			page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, cookies=True)
			link = 'http://pic4pay.com/' + re.search('"pic_id":"(\w+)"', page).group(1) + '.html'
			self.lock.acquire()
			print "Pic4PayCallback: {0}".format(link)
			slLinks.append(link)
			self.lock.release()
			return
		return

	def PicCashCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "PicCashCallback: processing {0}...".format(pic,)
			self.lock.release()
			curl = pycurl.Curl()
			srvc = 'PicCash.net'
			try:
				page = self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'), cookies=True)
			except:
				print "PicCashCallback: Error in authUrl\nPicCashCallback: try {0}".format(tries)
				continue
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic))]
			for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
				postData.append(tuple(item for item in equals.split('=')))
			page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, cookies=True)
			try:
				link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), page).group(1)
				self.lock.acquire()
				print "PicCashCallback: {0}".format(link)
				slLinks.append(link)
				self.lock.release()
				return
			except:
				print "PicCashCallback: Error in link\nPicCashCallback: try {0}".format(tries)
				continue
		return

	def PlatimZaFotoCallback(self, pic, slLinks = list()):
		for tries in range(0, TRIES):
			self.lock.acquire()
			print "PlatimZaFotoCallback: processing {0}...".format(pic,)
			self.lock.release()

			curl = pycurl.Curl()
			srvc = 'PlatimZaFoto.ru'
			page = self.get(self.imageHostersConfig.get(srvc, 'authUrl'), cookies=True)
			if not re.search("Location: /", page):
				try:
					check = re.search("document.getElementById\('check'\).value = '(.+)';", page).group(1)
				except:
					print "PlatimZaFotoCallback: Error in link\nPlatimZaFotoCallback: try {0}".format(tries)
					continue
				authData = self.imageHostersConfig.get(srvc, 'authData') + '&check=' + check
				self.post(self.imageHostersConfig.get(srvc, 'authUrl'), authData, cookies=True)
			page = self.get(self.imageHostersConfig.get(srvc, 'getUrl'), cookies=True)
			session = re.search("'PHPSESSID':'(\w+)',", page).group(1)
			postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (curl.FORM_FILE, pic)), ('PHPSESSID', session)]
			for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
				postData.append(tuple(item for item in equals.split('=')))
			page = self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData, cookies=True)
			link = 'http://platimzafoto.ru/' + re.search('"pic_id":"(\w+)"', page).group(1) + '.html'
			self.lock.acquire()
			print "PlatimZaFotoCallback: {0}".format(link)
			slLinks.append(link)
			self.lock.release()
			return
		return

	def post(self, url, postData, proxy=False, cookies=False, cnnttimeout=0, timeout=0):
		curl = pycurl.Curl()
		curl.setopt(curl.URL, url)
		curl.setopt(curl.NOSIGNAL, 1)
		if cnnttimeout:
			curl.setopt(curl.CONNECTTIMEOUT, timeout)
		else:
			curl.setopt(curl.CONNECTTIMEOUT, CONNECT_TIMEOUT)
		if timeout:
			curl.setopt(curl.TIMEOUT, timeout)
		else:
			curl.setopt(curl.TIMEOUT, GET_TIMEOUT)
		buf = cStringIO.StringIO()
		if cookies:
			curl.setopt(curl.COOKIEFILE, '/tmp/cookies.txt')
			curl.setopt(curl.COOKIEJAR, '/tmp/cookies.txt')
		curl.setopt(curl.WRITEFUNCTION, buf.write)
		curl.setopt(curl.HEADER, 1)
		curl.setopt(curl.POSTFIELDS, postData)
		if proxy:
			curl.setopt(curl.PROXY, '127.0.0.1')
			curl.setopt(curl.PROXYPORT, 9999)
			curl.setopt(curl.PROXYTYPE, curl.PROXYTYPE_SOCKS4)
		curl.perform()
		return buf.getvalue()

	def postFile(self, url, postData, proxy=False, cookies=False, cnnttimeout=0, timeout=0):
		curl = pycurl.Curl()
		curl.setopt(curl.URL, url)
		buf = cStringIO.StringIO()
		curl.setopt(curl.WRITEFUNCTION, buf.write)
		curl.setopt(curl.NOSIGNAL, 1)
		curl.setopt(curl.HEADER, 1)
		curl.setopt(curl.HTTPPOST, postData)
		if cnnttimeout:
			curl.setopt(curl.CONNECTTIMEOUT, timeout)
		else:
			curl.setopt(curl.CONNECTTIMEOUT, CONNECT_TIMEOUT)
		if timeout:
			curl.setopt(curl.TIMEOUT, timeout)
		else:
			curl.setopt(curl.TIMEOUT, GET_TIMEOUT)
		if proxy:
			curl.setopt(curl.PROXY, '127.0.0.1')
			curl.setopt(curl.PROXYPORT, 9999)
			curl.setopt(curl.PROXYTYPE, curl.PROXYTYPE_SOCKS4)
		if cookies:
			curl.setopt(curl.COOKIEFILE, '/tmp/cookies.txt')
			curl.setopt(curl.COOKIEJAR, '/tmp/cookies.txt')
		curl.perform()
		return buf.getvalue()

	def get(self, url, proxy=False, header=True, cnnttimeout=0, timeout=0, cookies=False):
		buf = cStringIO.StringIO()
		curl = pycurl.Curl()
		curl.setopt(curl.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36")
		curl.setopt(curl.COOKIE, "lang=en; user_lang=en; lang_current=en")
		curl.setopt(curl.URL, url)
		curl.setopt(curl.FOLLOWLOCATION, 1)
		curl.setopt(curl.NOSIGNAL, 1)
		if cnnttimeout:
			curl.setopt(curl.CONNECTTIMEOUT, timeout)
		else:
			curl.setopt(curl.CONNECTTIMEOUT, CONNECT_TIMEOUT)
		if timeout:
			curl.setopt(curl.TIMEOUT, timeout)
		else:
			curl.setopt(curl.TIMEOUT, GET_TIMEOUT)
		if cookies:
			curl.setopt(curl.COOKIEFILE, '/tmp/cookies.txt')
			curl.setopt(curl.COOKIEJAR, '/tmp/cookies.txt')
		curl.setopt(curl.WRITEFUNCTION, buf.write)
		if not header:
			curl.setopt(curl.HEADER, 0)
		else:
			curl.setopt(curl.HEADER, 1)
		if proxy:
			curl.setopt(curl.PROXY, proxy)
		curl.perform()
		curl.close()
		return buf.getvalue()
