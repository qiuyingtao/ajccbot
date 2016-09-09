# coding=utf-8

import urllib
import urllib2
import time
import twitter

enable_proxy = False
proxy_handler = urllib2.ProxyHandler({"http" : 'http://192.168.1.1:8080'})
null_proxy_handler = urllib2.ProxyHandler({})
if enable_proxy:
    opener = urllib2.build_opener(proxy_handler)
else:
    opener = urllib2.build_opener(null_proxy_handler)

url = 'http://www.ccdi.gov.cn/ajcc/index'
lastUrl = 'http://www.ccdi.gov.cn/ajcc/201407/t20140716_25237.html'
LOOP = True
interval = 5

access_token = '2.004LDAhF0JSg1w8dffa4aa7007f9HL'
post_url = 'https://api.weibo.com/2/statuses/update.json'

tw_api = twitter.Api(consumer_key='mO6VkXbQpaRYb9AmAKYd0w7pI',
                     consumer_secret='Pj615gQfe8IPKbKHqiOsE5zZN83Oslj0ecUYlrJaXgUTJ7gJRn',
                     access_token_key='2647994180-GWW2dATFXRJkopj9cey4ZEe5YLh0urwCbEIZLzH',
                     access_token_secret='eE7j8jGrixAoRkVTawRJ9Ls3aLDB4LBVsUDCGyvPTEvij')

while LOOP:
    hasAvailableLi = True
    urlandtxtList = []
    page = 1

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
        for (urlItem,txtItem) in reversed(urlandtxtList):
            timeStr = time.strftime('%Y-%m-%d %H:%M',time.gmtime(time.time()+8*60*60)) #东八区
            msgWeibo = u'%s，来源：%s，更新时间：%s #中纪委案件查处#' % (txtItem, urlItem, timeStr)
            msgTweet = u'%s，来源：%s，更新时间：%s #中纪委案件查处' % (txtItem, urlItem, timeStr)
            #print msg
            post_data = urllib.urlencode({'access_token' : access_token, 'status' : msgWeibo.encode('utf-8')})
            r = urllib2.urlopen(post_url, post_data)
            print r.read()
            '''
            results = tw_api.PostUpdate(msgTweet.encode('utf-8'))
            print results
            '''

    print time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))

    time.sleep(interval * 60)
