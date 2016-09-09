# coding=gbk

import urllib
import urllib2
import time

enable_proxy = True
proxy_handler = urllib2.ProxyHandler({"http" : 'http://192.168.107.61:3128'})
null_proxy_handler = urllib2.ProxyHandler({})
if enable_proxy:
    opener = urllib2.build_opener(proxy_handler)
else:
    opener = urllib2.build_opener(null_proxy_handler)

url = 'http://www.ccdi.gov.cn/ajcc/index'
LOOP = True
interval = 5
lastUrl = 'http://www.ccdi.gov.cn/ajcc/201407/t20140712_25101.html'
#lastUrl = 'http://www.ccdi.gov.cn/ajcc/201407/t20140701_24732.html'
page = 1
access_token = '2.004LDAhF0JSg1w8dffa4aa7007f9HL'

while LOOP:
    hasAvailableLi = True
    urlandtxtList = []

    response = opener.open(url +'.html', timeout = 120)
    #htmldata = response.read()
    htmldata = response.read().decode('utf8')
    #print htmldata
    ulStartIndex = htmldata.find('<ul class="list_news_dl">')
    ulEndIndex = htmldata.find('</ul>')
    ulStr = htmldata[ulStartIndex:ulEndIndex+5]
    #print ulStr
    while hasAvailableLi:
        liStartIndex = ulStr.find('<li')
        if liStartIndex == -1:
            response = opener.open(url + '_' + str(page) + '.html', timeout = 120)
            htmldata = response.read().decode('utf8')
            ulStartIndex = htmldata.find('<ul class="list_news_dl">')
            ulEndIndex = htmldata.find('</ul>')
            ulStr = htmldata[ulStartIndex:ulEndIndex+5]
            #print ulStr
            page = page + 1
            liStartIndex = ulStr.find('<li')
        liEndIndex = ulStr.find('</li>')
        liStr = ulStr[liStartIndex:liEndIndex+5]
        #print liStr
        linkUrlStartIndex = liStr.find('<a href=')
        linkUrlEndIndex = liStr.find('target=')
        liStr2 = liStr[linkUrlEndIndex:]
        linkTxtStartIndex = liStr2.find('">')
        linkTxtEndIndex = liStr2.find('</a>')
        linkUrl = str('http://www.ccdi.gov.cn/ajcc' + liStr[linkUrlStartIndex+10:linkUrlEndIndex-2])
        linkTxt = liStr2[linkTxtStartIndex+2:linkTxtEndIndex]
        if lastUrl != linkUrl:
            urlandtxtList.append((linkUrl, linkTxt))
            ulStr = ulStr[liEndIndex+5:]
        elif len(urlandtxtList) != 0:
            lastUrl = urlandtxtList[0][0]
            hasAvailableLi = False
        else:
            hasAvailableLi = False

    if len(urlandtxtList) != 0:
        for (urlItem,txtItem) in urlandtxtList:
            timeStr = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time())) 
            msg = u'%s，来源：%s，更新时间：%s #中纪委案件查处#'  % (txtItem, urlItem, timeStr)
            #print msg 
            post_data = urllib.urlencode({'access_token' : access_token, 'status' : msg.encode('utf-8') })

            post_url = 'https://api.weibo.com/2/statuses/update.json'
            r = urllib2.urlopen(post_url, post_data);
            print r.read()

    print time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time())) 

    time.sleep(interval * 60)