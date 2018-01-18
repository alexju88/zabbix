#coding:utf-8

import urllib
import smtplib
import sys
import subprocess

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart  
from email.utils import parseaddr, formataddr

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

from_addr = "icfme@ford.com"
password = "111111"
to_addr = "wju@cfme.ford.com"
smtp_server = "19.229.0.19"

zabbix_server = "cne0at09"
graph_path = "/etc/zabbix/zabbix/mail"
itemid = int(27885)
eventdate = "2018.01.18"
eventtime = "13:14:57"
itemname1 = "test"
itemvalue1 = "test"

#获取传入的参数

itemid = int(sys.argv[1])
hostname1 = sys.argv[2]
triggername = sys.argv[3]
itemvalue1 = sys.argv[4]
eventdate = str(sys.argv[5])
eventtime = str(sys.argv[6])
itemname1 = sys.argv[7]
itemvalue1 = sys.argv[8]

#zabbix"最新数据"图形的通用地址

graph_url = "http://%s/zabbix/chart.php?period=43200&isNow=1&itemids=%d&type=0&profileIdx=web.item.graph&profileIdx2=26157&width=1228" % (zabbix_server,itemid)
graph_location = '%s/%d.jpg' %(graph_path,itemid)
#subprocess.call('wget %s --no-proxy -O %s/%s.jpg' % (graph_url,graph_path,itemid))
urllib.urlretrieve(graph_url,graph_location)

#HTML构造
content = '<html><body><p><font size="2" face="微软雅黑" color="red"><strong><span style="line-height:1;">Zabbix警报:</span></strong></font></p><br /><font size="2" face="微软雅黑" color="red"><strong><span style="line-height:1;">告警时间:</span></strong>%s %s</font><br /><font size="2" face="微软雅黑" color="red"><strong><span style="line-height:1;">当前:</span></strong>%s: %s</font><br /><img width="1344" height="382" src="cid:test"></body></html>' % (eventdate,eventtime,itemname1,itemvalue1)

#邮件图片构造
def addimg(src,imgid):  
    fp = open(src, 'rb')  
    msgImage = MIMEImage(fp.read())  
    #fp.close()  
    msgImage.add_header('Content-ID', imgid)
    return msgImage  
#fp = open(graph_location,'rb')
#msgImage = MIMEImage(fp.read())
#msgImage.add_header('Content-ID','test')

msg = MIMEMultipart('related')  
msgtext = MIMEText(content,'html', 'utf-8')
msg.attach(msgtext)  
msg.attach(addimg(graph_location,'test'))

msg['From'] = _format_addr('Python <%s>' % from_addr)
msg['To'] = _format_addr('Admin <%s>' % to_addr)
msg['Subject'] = Header('Zabbix:%s %s %s' % (hostname1,triggername,itemvalue1), 'utf-8').encode()

try: 
	server = smtplib.SMTP(smtp_server, 25)
	server.set_debuglevel(1)
	server.sendmail(from_addr, [to_addr], msg.as_string())
	print 'mail send!'
	server.quit()
except Exception, e:
	print "failed!"+str(e)



#构造附件
#att = MIMEText(open('Pictures.rar','rb').read(),'base64','utf-8')
#att["Content-Type"] = 'application/octet-stream'
#att["Content-Disposition"] = 'attatchment;filename="Pictures.rar"'
#msg.attach(att)
#smtp = smtplib.SMTP()
#smtp.connect('smtp.126.com')
#smtp.login(username,password)
#smtp.sendmail(sender,receiver,msg.as_string())
#smtp.quit()

