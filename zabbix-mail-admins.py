#!/usr/bin/python2
#coding:utf-8
#wju@ford.com

#-------------------------------------------------------mail------------------------------------------------
#mail module
import requests
import smtplib,os,time,re
import urllib
import email
import sys

#solve utf8 
reload(sys)
sys.setdefaultencoding('utf8')

#wechat module
import json
import urllib2
import ssl
#Disable SSL
if hasattr(ssl, '_create_unverified_context'):
	ssl._create_default_https_context = ssl._create_unverified_context

#mail import
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart  
from email.utils import parseaddr, formataddr

#global settings
USER='Admin'
PASSWD='xxxx'
PERIOD='3600'
WIDTH='600'
FROM_ADDRESS = "xxxx@xxxx.com"
TO_ADDRESS = ['xxxx@xxxx.com']
SMTP_SERVER = "xxxx"
ZABBIX_SERVER = "xxxx"
GRAPH_LOCATION = "/tmp/zabbix/"
#list of users split with |, less than 1000。"@all" is supported.
USERID=['xxx']

ID="xxxx"
Secret="xxxxxxxxxxxxxxxxxxxxxxxxxx"
#list of depts split with |, less than 100。
#Not work when user is set to be "@all".
PARTYID= 666
## application id.default setting is enterprise assistant.
AppID = 1000003  

#get parameters from zabbix actions
itemid = int(sys.argv[1])
hostname1 = str(sys.argv[2])
triggername = str(sys.argv[3])
itemvalue1 = str(sys.argv[4])
eventdate = str(sys.argv[5])
eventtime = str(sys.argv[6])
itemname1 = str(sys.argv[7])
itemvalue1 = str(sys.argv[8])
type = str(sys.argv[9])
'''
#test data
hostname1='hostname1'
triggername='triggername'
itemid = int(27885)
eventdate = "2018.01.18"
eventtime = "13:14:57"
itemname1 = "itemname1"
itemvalue1 = "itemvalue1"
type='警报'
'''

if type == '警报':
    fontcolor='red'
else:
    fontcolor='green'

f=open('/var/log/zabbix/zabbix_actions.log','a')
print >>f,time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid +'...start setting'


#format email address
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def get_graph(itemID,pName=None):
    myRequests = requests.Session()
    try:
        loginUrl = "http://%s/zabbix/index.php" % ZABBIX_SERVER
        #print loginUrl
        loginHeaders={
            "Host":ZABBIX_SERVER,
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        playLoad = {
            "name":USER,
            "password":PASSWD,
            "autologin":"1",
            "enter":"Sign in",
        }
        res = myRequests.post(loginUrl,headers=loginHeaders,data=playLoad)
         
        testUrl = "http://%s/zabbix/chart.php" % ZABBIX_SERVER
        testUrlplayLoad = {
            "period" :PERIOD,
            "itemids[0]" : itemID,	
            "type" : "0",
            "profileIdx" : "web.item.graph",
            "width" : WIDTH,
        }
        testGraph = myRequests.get(url=testUrl,params=testUrlplayLoad)
        IMAGEPATH = os.path.join(GRAPH_LOCATION,pName)
        f = open(IMAGEPATH,'wb')
        f.write(testGraph.content)
        f.close()	
        pName = GRAPH_LOCATION + pName
        return pName
    except Exception as e:
        print e
        return False
		

#build picture
def addimg(src,imgid):  
    fp = open(src,'rb')  
    msgImage = MIMEImage(fp.read(),_subtype='')
    fp.close()  
    msgImage.add_header('Content-ID',imgid)
    return msgImage

#do it
if __name__ == '__main__':
  print >>f,time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid +'...start building'
  #HTML build graph
  content = '<html><body><font size="2" face="微软雅黑" color="%s"><strong>主机: </strong>%s</font><br /><font size="2" face="微软雅黑" color="%s"><strong>时间: </strong>%s %s</font><br /><font size="2" face="微软雅黑" color="%s"><strong>当前: </strong>%s: %s</font><br /><img width="770" height="400" src="cid:image"></body></html>' % (fontcolor,hostname1,fontcolor,eventdate,eventtime,fontcolor,itemname1,itemvalue1)
  #picture named as time	
  time_tag=time.strftime("%Y%m%d%H%M%S", time.localtime())
  picture_name=time_tag + "_" + str(itemid) +".png"
  print >>f, time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid + '...start graphing'
  #HTML build text and graph
  msg = MIMEMultipart('related')  
  msgtext = MIMEText(content,'html','utf-8')
  msg.attach(msgtext)
  msg.attach(addimg(get_graph(itemid,picture_name),'<image>'))
  print >>f, time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid+'...end graphing' 
  #mail format
  for user in TO_ADDRESS:
    msg['From'] = _format_addr('Python <%s>' % FROM_ADDRESS)
    msg['To'] = _format_addr('Admin <%s>' % user)
    msg['Subject'] = Header('%s:%s %s %s' % (type,hostname1,triggername,itemvalue1), 'utf-8').encode()
    server = smtplib.SMTP(SMTP_SERVER, 25)
    server.sendmail(FROM_ADDRESS, user, msg.as_string())
    server.quit()
    print >>f, time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid +'...email send to %s' % user

#-------------------------------------------------------wechat------------------------------------------------
# Get TOKEN
def get_token():  
    gurl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(ID, Secret)
    r=requests.get(gurl)
    dict_result= (r.json())
    return dict_result['access_token']
	
	
# upload temp picture 
def get_media_ID(path):  
    Gtoken = get_token()
    img_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={}&type=image".format(Gtoken)
    files = {'image': open(path, 'rb')}
    r = requests.post(img_url, files=files)
    re = json.loads(r.text)
    return re['media_id']

#send text
def  send_text(text,user): 
    post_data = {}
    msg_content = {}
	#less than 2048 bytes
    msg_content['content'] = text  
    post_data['touser'] = user
    post_data['toparty'] = PARTYID
    post_data['msgtype'] = 'text'
    post_data['agentid'] = AppID
    post_data['text'] = msg_content
	#secret 0
    post_data['safe'] = '0'  
    Gtoken = get_token()
    purl1="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(Gtoken)
    json_post_data = json.dumps(post_data,False,False)
    request_post = urllib2.urlopen(purl1,json_post_data.encode(encoding='UTF8'))
    return request_post

# send picture
def  send_picture(path,user):  
    img_id = get_media_ID(path)
    post_data1 = {}
    msg_content1 = {}
    msg_content1['media_id'] = img_id
    post_data1['touser'] = user
    post_data1['toparty'] = PARTYID
    post_data1['msgtype'] = 'image'
    post_data1['agentid'] = AppID
    post_data1['image'] = msg_content1
    post_data1['safe'] = '0'
    Gtoken = get_token()
    purl2="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(Gtoken)
    json_post_data1 = json.dumps(post_data1,False,False)
    request_post = urllib2.urlopen(purl2,json_post_data1.encode(encoding='UTF8'))
    return request_post


for user in USERID:
	#send text
	wechat_text = "%s:%s %s\n当前:%s\n时间:%s %s" % (type,hostname1,triggername,itemvalue1,eventdate,eventtime)
	send_text(wechat_text,user)
	print >>f, time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid + '...wechat text send to %s'% user
	#send picture
	wechat_picture = get_graph(itemid,picture_name)
	send_picture(wechat_picture,user)
	print >>f, time.strftime("%Y%m%d %H:%M:%S", time.localtime())+' %s' % itemid + '...wechat picture send to %s'% user

f.close()
