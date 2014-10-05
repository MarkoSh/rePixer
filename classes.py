#!/usr/bin/env python

import sys, os, ftplib, ConfigParser, MySQLdb, cStringIO, pycurl, re, datetime, time, urllib, threading, socket, random
import hashlib


class rePixer:
    sqlConfig = 0
    siteFtpConfig = 0
    mysqlConnect = 0
    mysqlCursor = 0
    section = 0
    ftp = 0
    buf = 0
    curl = 0
    imageHostersConfig = 0
    callback = dict()
    picsList = list()
    pics = 0
    # callbacks
    def PicForAllCallback(self, srvc, pic):
        self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'))
        tst = self.buf.getvalue()
        postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
        for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
            postData.append(tuple(item for item in equals.split('=')))
        self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
        tst = self.buf.getvalue()
        try:
            link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
            self.picsList.append(link)
            print "\t%s works good" % srvc
            print "\t%s" % link
        except:
            print "\t%s ERROR IN LINK ##########" % srvc
        return

    def PlatimZaFotoCallback(self, srvc, pic):
        self.get(self.imageHostersConfig.get(srvc, 'authUrl'))
        tst = self.buf.getvalue()
        try:
            if not re.search('Location: /', self.buf.getvalue()):
                check = re.search("document.getElementById\('check'\).value = '(.+)';", self.buf.getvalue()).group(1)
                authData = self.imageHostersConfig.get(srvc, 'authData') + '&check=' + check
                self.post(self.imageHostersConfig.get(srvc, 'authUrl'), authData)
                tst = self.buf.getvalue()
            self.get(self.imageHostersConfig.get(srvc, 'getUrl'))
            tst = self.buf.getvalue()
            try:
                session = re.search("'PHPSESSID':'(\w+)',", self.buf.getvalue()).group(1)
                postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic)),
                            ('PHPSESSID', session)]
                for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
                    postData.append(tuple(item for item in equals.split('=')))
                self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
                tst = self.buf.getvalue()
                try:
                    link = 'http://platimzafoto.ru/' + re.search('"pic_id":"(\w+)"', self.buf.getvalue()).group(
                        1) + '.html'
                    self.picsList.append(link)
                    print "\t%s works good" % srvc
                    print "\t%s" % link
                except:
                    print "\t%s ERROR IN LINK ##########" % srvc
            except:
                print "\t%s ERROR IN SESSION ##########" % srvc
        except:
            print "\t%s ERROR IN CHECK ##########" % srvc
        return

    def PicCashCallback(self, srvc, pic):
        self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'))
        postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
        for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
            postData.append(tuple(item for item in equals.split('=')))
        self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
        tst = self.buf.getvalue()
        try:
            link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
            self.picsList.append(link)
            print "\t%s works good" % srvc
            print "\t%s" % link
        except:
            print "\t%s ERROR IN LINK ##########" % srvc
        return

    def Pic4PayCallback(self, srvc, pic):
        self.get(self.imageHostersConfig.get(srvc, 'authUrl'))
        tst = self.buf.getvalue()
        try:
            if not re.search('Location: /', self.buf.getvalue()):
                self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'))
                tst = self.buf.getvalue()
            self.get(self.imageHostersConfig.get(srvc, 'getUrl'))
            tst = self.buf.getvalue()
            session = re.search("'PHPSESSID':'(\w+)'", self.buf.getvalue()).group(1)
            postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic)),
                        ('PHPSESSID', session)]
            self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
            tst = self.buf.getvalue()
            try:
                link = 'http://pic4pay.com/' + re.search('"pic_id":"(\w+)"', self.buf.getvalue()).group(1) + '.html'
                self.picsList.append(link)
                print "\t%s works good" % srvc
                print "\t%s" % link
            except:
                print "\t%s ERROR IN LINK ##########" % srvc
        except:
            print "\t%s ERROR IN SESSION ##########" % srvc
        return

    def Pic4YouCallback(self, srvc, pic, tries=0):
        if tries < 10:
            self.post(self.imageHostersConfig.get(srvc, 'authUrl'), self.imageHostersConfig.get(srvc, 'authData'))
            tst = self.buf.getvalue()
            postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
            for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
                postData.append(tuple(item for item in equals.split('=')))
            try:
                self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
                tst = self.buf.getvalue()
                try:
                    link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
                    self.picsList.append(link)
                    print "\t%s works good" % srvc
                    print "\t%s" % link
                except:
                    print "\t%s ERROR IN LINK ##########" % srvc
            except pycurl.error, err:
                print "Try: {0}, error: {1} - {2}".format(tries, err[0], err[1])
                tries += 1
                self.Pic4YouCallback(srvc, pic, tries)
                return 1
        return

    def Image2YouCallback(self, srvc, pic):
        self.get(self.imageHostersConfig.get(srvc, 'getUrl'))
        tst = self.buf.getvalue()
        self.get(self.imageHostersConfig.get(srvc, 'authUrl'))
        tst = self.buf.getvalue()
        self.get(self.imageHostersConfig.get(srvc, 'getUrl'))
        tst = self.buf.getvalue()
        self.get(self.imageHostersConfig.get(srvc, 'getUrl2'))
        tst = self.buf.getvalue()
        try:
            session = re.search("'session': '(.+)'", self.buf.getvalue()).group(1)
            postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
            for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
                equals = re.sub('\{pic\}', pic, equals)
                equals = re.sub('\{session\}', session, equals)
                postData.append(tuple(item for item in equals.split('=')))
            self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
            tst = self.buf.getvalue()
            self.get(self.imageHostersConfig.get(srvc, 'getUrlWithPic'))
            tst = self.buf.getvalue()
            try:
                link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
                self.picsList.append(link)
                print "\t%s works good" % srvc
                print "\t%s" % link
            except:
                print "\t%s ERROR IN LINK ##########" % srvc
        except:
            print "\t%s ERROR IN SESSION ##########" % srvc
        return

    def ImageVenueCallback(self, srvc, pic):
        postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
        for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
            postData.append(tuple(item for item in equals.split('=')))
        self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
        try:
            link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
            self.picsList.append(link)
            print "\t%s works good" % srvc
            print "\t%s" % link
        except:
            print "\t%s ERROR IN LINK ##########" % srvc
        return

    def PicSeeCallback(self, srvc, pic, tries=0):
        if tries < 10:
            postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
            try:
                self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
                tst = self.buf.getvalue()
                try:
                    link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
                    self.picsList.append(link)
                    print "\t%s works good" % srvc
                    print "\t%s" % link
                except:
                    print "\t%s ERROR IN LINK ##########" % srvc
            except pycurl.error, err:
                print "Try: {0}, error: {1} - {2}".format(tries, err[0], err[1])
                tries += 1
                self.PicSeeCallback(srvc, pic, tries)
                return 1
        return

    def iPictureCallback(self, srvc, pic):
        postData = [(self.imageHostersConfig.get(srvc, 'filePostField'), (self.curl.FORM_FILE, pic))]
        for equals in str(self.imageHostersConfig.get(srvc, 'additionalPostData')).split('&'):
            postData.append(tuple(item for item in equals.split('=')))
        self.postFile(self.imageHostersConfig.get(srvc, 'postUrl'), postData)
        try:
            refreshUrl = re.search(self.imageHostersConfig.get(srvc, 'refreshUrlRx'), self.buf.getvalue()).group(1)
            self.get(refreshUrl)
            tst = self.buf.getvalue()
            try:
                link = re.search(self.imageHostersConfig.get(srvc, 'picLinkRx'), self.buf.getvalue()).group(1)
                self.picsList.append(link)
                print "\t%s works good" % srvc
                print "\t%s" % link
            except:
                print "\t%s ERROR IN LINK ##########" % srvc
        except:
            print "\t%s ERROR IN REFRESHURL ##########" % srvc
        return

    # /callbacks

    def __init__(self, sqlConfig, siteFtpConfig, imageHostersConfig):
        self.sqlConfig = sqlConfig
        self.siteFtpConfig = siteFtpConfig
        host = self.sqlConfig.get("MySQL", "host")
        user = self.sqlConfig.get("MySQL", "user")
        password = self.sqlConfig.get("MySQL", "password")
        db = self.sqlConfig.get("MySQL", "db")
        self.mysqlConnect = MySQLdb.connect(host, user, password, db)
        self.mysqlCursor = self.mysqlConnect.cursor()
        self.ftp = ftplib.FTP()
        self.buf = cStringIO.StringIO()
        self.imageHostersConfig = imageHostersConfig
        self.curl = pycurl.Curl()
        self.callback['iPictureCallback'] = self.iPictureCallback
        self.callback['PicSeeCallback'] = self.PicSeeCallback
        self.callback['ImageVenueCallback'] = self.ImageVenueCallback
        self.callback['Image2YouCallback'] = self.Image2YouCallback
        self.callback['Pic4YouCallback'] = self.Pic4YouCallback
        self.callback['Pic4PayCallback'] = self.Pic4PayCallback
        self.callback['PicCashCallback'] = self.PicCashCallback
        self.callback['PlatimZaFotoCallback'] = self.PlatimZaFotoCallback
        self.callback['PicForAllCallback'] = self.PicForAllCallback
        return

    def repixOld(self):
        self.getSlListOld()
        return

    def getSlListOld(self):
        self.mysqlCursor.execute(
            "SELECT `id`, `title_en`, `modified`, `screenlist` FROM `f3x_posts` WHERE `id` < 15986 AND `screenlist` LIKE '%picsee.net%' AND `repix` = 1 ORDER BY `id` DESC LIMIT 0,3000")
        self.mysqlConnect.commit()
        self.pixDownlowderOld()
        return

    def pixDownlowderOld(self):
        if not os.path.exists('/tmp/repixer'):
            os.mkdir('/tmp/repixer')
        os.chdir('/tmp/repixer')
        print "Starting repixing..."
        for data in self.mysqlCursor.fetchall():
            print "Current post: %s" % data[0]
            for string in str(data[3]).split('|'):
                if re.search("picsee.net", string):
                    try:
                        print "Original link is: %s" % string
                        #print "Parsing host..."
                        #host = re.search("(http://img(\d+)\.imagevenue\.com/)", string).group(0)
                        #print "Host is: %s" % host
                        self.get(string, True)
                        page = self.buf.getvalue()
                        try:
                            #print "Parsing SRC..."
                            #link = host + re.search("SRC=\"(.*)\" alt", page).group(1)
                            #link = "http://image2you.ru/allimages/" + re.search("(/allimages/(\d+)_(_img_(\d+)_([a-z0-9]+)_(\d+).jpeg))", page).group(3)
                            if not re.search("Content-Length:0", page):
                                link = "http://anonymouse.org/cgi-bin/anon-www.cgi/" + string
                                print "Link is: %s" % link
                                print "Getting pic..."
                                timestamp = "%i" % time.mktime(data[2].timetuple())
                                picName = timestamp + "_sl_" + re.sub("( |:|,|'|\!|\&|\?)", "_", str(data[1]).lower())[
                                                               :30] + ".jpeg"
                                try:
                                    urllib.urlretrieve(link, picName)
                                    print "Getting pic...Done"
                                    self.uploadToSrv(picName)
                                    print "Deleting pic..."
                                    os.unlink(picName)
                                    print "Deleting pic...Done"
                                    if len(self.picsList) > 5:
                                        self.pics = self.implode('|', self.picsList)
                                        self.updateDb(data[0], 2)
                                except:
                                    print "ERROR IN GETTING LINK"
                            else:
                                print "PIC IS DEAD"
                        except:
                            print "ERROR IN PARSING SRC"
                    except:
                        print "ERROR IN PARSING HOST"
        print "Starting repixing...Done"
        return

    def repixMe(self):
        self.getSlList()
        return

    def getSlList(self):
        self.mysqlCursor.execute(
            "SELECT `id`, `screenlist` FROM `f3x_posts` WHERE `repix` = 0 ORDER BY `id` DESC LIMIT 0,3000")
        self.mysqlConnect.commit()
        self.ftpPixDownlowder()
        return self

    def ftpPixDownlowder(self):
        if not os.path.exists('/tmp/repixer'):
            os.mkdir('/tmp/repixer')
        os.chdir('/tmp/repixer')
        for section in self.siteFtpConfig.sections():
            print "Starting repixing..."
            for data in self.mysqlCursor.fetchall():
                print "Current post: %s" % data[0]
                print "\tCopying file: %s..." % data[1][2:]
                self.section = section
                print "\tConnecting to host: %s" % self.siteFtpConfig.get(self.section, 'host')
                self.ftp.connect(self.siteFtpConfig.get(self.section, 'host'))
                self.ftp.login(self.siteFtpConfig.get(self.section, 'user'),
                               self.siteFtpConfig.get(self.section, 'password'))
                self.ftp.cwd(self.siteFtpConfig.get(self.section, 'folder'))
                try:
                    self.ftp.retrbinary('RETR ' + data[1][2:], open(os.path.basename(data[1]), 'wb').write)
                except EOFError:
                    print "\tRe-Connecting to host: %s" % self.siteFtpConfig.get(self.section, 'host')
                    self.ftp.connect(self.siteFtpConfig.get(self.section, 'host'))
                    self.ftp.login(self.siteFtpConfig.get(self.section, 'user'),
                                   self.siteFtpConfig.get(self.section, 'password'))
                    self.ftp.cwd(self.siteFtpConfig.get(self.section, 'folder'))
                    print "\tCopying file: %s..." % data[1]
                    self.ftp.retrbinary('RETR ' + data[1][2:], open(os.path.basename(data[1]), 'wb').write)
                self.ftp.close()
                print "\tCopying file: %s...Done" % data[1][2:]
                self.uploadToSrv(os.path.basename(data[1]))
                if len(self.picsList) > 5:
                    self.pics = self.implode('|', self.picsList)
                    self.updateDb(data[0])
                    print "\tRemoving remote file: %s..." % data[1][2:]
                    self.section = section
                    print "\tConnecting to host: %s" % self.siteFtpConfig.get(self.section, 'host')
                    self.ftp.connect(self.siteFtpConfig.get(self.section, 'host'))
                    self.ftp.login(self.siteFtpConfig.get(self.section, 'user'),
                                   self.siteFtpConfig.get(self.section, 'password'))
                    self.ftp.cwd(self.siteFtpConfig.get(self.section, 'folder'))
                    try:
                        print "\tProcess..."
                        self.ftp.delete(data[1][2:])
                    except EOFError:
                        self.ftp.close()
                        print "\tRe-Connecting to host: %s" % self.siteFtpConfig.get(self.section, 'host')
                        self.ftp.connect(self.siteFtpConfig.get(self.section, 'host'))
                        self.ftp.login(self.siteFtpConfig.get(self.section, 'user'),
                                       self.siteFtpConfig.get(self.section, 'password'))
                        self.ftp.cwd(self.siteFtpConfig.get(self.section, 'folder'))
                        self.ftp.delete(data[1][2:])
                    self.ftp.close()
                    print "\tRemoving remote file: %s...Done" % data[1][2:]
                else:
                    print "Not enough mirrors..."
            print "Starting repixing...Done"
        return

    def updateDb(self, id, status=1):
        print "\tUpdating post in db..."
        sql = "UPDATE `f3x_posts` SET `repix` = %s, `screenlist` = '%s' WHERE `id` = %s" % (status, self.pics, id)
        self.mysqlCursor.execute(sql)
        self.mysqlConnect.commit()
        print "\tUpdating post in db...Done"
        print "\tCaching post http://free-3x.com/#post-%s..." % id
        self.get("http://free-3x.com/showPost/%s/ajax" % id)
        print "\tCaching post http://free-3x.com/#post-%s...Done" % id
        self.picsList = list()
        return

    def implode(self, delimiter, list):
        list = set(list)
        string = ""
        seq = len(list)
        for item in range(0, seq):
            string += list[item]
            if (item + 1) < len(list):
                string += delimiter
        return string

    def uploadToSrv(self, pic):
        print "\tUploading file: %s..." % pic
        for srvc in self.imageHostersConfig.sections():
            try:
                if self.imageHostersConfig.get(srvc, 'disabled'):
                    continue
            except:
                self.callback[self.imageHostersConfig.get(srvc, 'callback')](srvc, pic)
        print "\tUploading file: %s...Done" % pic
        return

    def get(self, url, proxy=False, header=True):
        self.curl = pycurl.Curl()
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.COOKIEFILE, '/tmp/cookies.txt')
        self.curl.setopt(self.curl.COOKIEJAR, '/tmp/cookies.txt')
        self.buf.truncate(0)
        self.curl.setopt(self.curl.WRITEFUNCTION, self.buf.write)
        if not header:
            self.curl.setopt(self.curl.HEADER, 0)
        else:
            self.curl.setopt(self.curl.HEADER, 1)
        if proxy:
            self.curl.setopt(self.curl.PROXY, '127.0.0.1')
            self.curl.setopt(self.curl.PROXYPORT, 9999)
            self.curl.setopt(self.curl.PROXYTYPE, self.curl.PROXYTYPE_SOCKS4)
        self.curl.perform()
        self.curl.close()
        return self

    def post(self, url, postData, proxy=False):
        self.curl = pycurl.Curl()
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.COOKIEFILE, '/tmp/cookies.txt')
        self.curl.setopt(self.curl.COOKIEJAR, '/tmp/cookies.txt')
        self.buf.truncate(0)
        self.curl.setopt(self.curl.WRITEFUNCTION, self.buf.write)
        self.curl.setopt(self.curl.HEADER, 1)
        self.curl.setopt(self.curl.POSTFIELDS, postData)
        if proxy:
            self.curl.setopt(self.curl.PROXY, '127.0.0.1')
            self.curl.setopt(self.curl.PROXYPORT, 9999)
            self.curl.setopt(self.curl.PROXYTYPE, self.curl.PROXYTYPE_SOCKS4)
        self.curl.perform()
        return self

    def postFile(self, url, postData, proxy=False):
        self.curl = pycurl.Curl()
        self.curl.setopt(self.curl.URL, url)
        self.curl.setopt(self.curl.COOKIEFILE, '/tmp/cookies.txt')
        self.curl.setopt(self.curl.COOKIEJAR, '/tmp/cookies.txt')
        self.buf.truncate(0)
        self.curl.setopt(self.curl.WRITEFUNCTION, self.buf.write)
        self.curl.setopt(self.curl.HEADER, 1)
        self.curl.setopt(self.curl.HTTPPOST, postData)
        if proxy:
            self.curl.setopt(self.curl.PROXY, '127.0.0.1')
            self.curl.setopt(self.curl.PROXYPORT, 9999)
            self.curl.setopt(self.curl.PROXYTYPE, self.curl.PROXYTYPE_SOCKS4)
        self.curl.perform()
        return self
