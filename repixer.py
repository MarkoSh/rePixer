#!/usr/bin/env python

from classes_2 import *

if not os.path.exists(os.path.expanduser('~') + '/.repixer'):
	os.mkdir(os.path.expanduser('~') + '/.repixer')
if not os.path.exists(os.path.expanduser('~') + '/.repixer/remote-mysql.cfg'):
	open(os.path.expanduser('~') + '/.repixer/remote-mysql.cfg', 'w+')
if not os.path.exists(os.path.expanduser('~') + '/.repixer/site-ftp.cfg'):
	open(os.path.expanduser('~') + '/.repixer/site-ftp.cfg', 'w+')
if not os.path.exists(os.path.expanduser('~') + '/.repixer/image-hosters.cfg'):
	open(os.path.expanduser('~') + '/.repixer/image-hosters.cfg', 'w+')

sqlConfig = ConfigParser.RawConfigParser()
sqlConfig.read(os.path.expanduser('~') + '/.repixer/remote-mysql.cfg')

siteFtpConfig = ConfigParser.RawConfigParser()
siteFtpConfig.read(os.path.expanduser('~') + '/.repixer/site-ftp.cfg')

imageHostersConfig = ConfigParser.RawConfigParser()
imageHostersConfig.read(os.path.expanduser('~') + '/.repixer/image-hosters.cfg')

dateStart = datetime.datetime.now()
repixer = rePixer(sqlConfig, siteFtpConfig, imageHostersConfig)
repixer.repixMe()
#repixer.repixOld()
dateEnd = datetime.datetime.now()
diff = time.strftime('%H:%M:%S', time.gmtime(round((dateEnd - dateStart).total_seconds(), 0)))
cmd = 'echo "All pix repixed in ' + diff + ', My Lordy" | mail -s "Repix done" -a "From: vps2@vps2.vps2" markhost@yandex.ru'
os.system(cmd)
