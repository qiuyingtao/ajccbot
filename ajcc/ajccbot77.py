# coding=utf-8

import ConfigParser
import urllib
import urllib2
import time
import re
import twitter

def broadcast(access_token, post_url, tw_api, msgWeibo, msgTweet):
    post_data = urllib.urlencode({'access_token' : access_token, 'status' : msgWeibo.encode('utf-8')})
    r = urllib2.urlopen(post_url, post_data)
    print r.read()

    results = tw_api.PostUpdate(msgTweet.encode('utf-8'))
    print results

def heartbeat(latest_time, access_token, post_url, tw_api):
    currentDateTime = time.strftime('%Y-%m-%d %H:%M',time.gmtime(time.time()+8*60*60)) #取得当前时间
    msgWeibo = u'#中纪委案件查处# 播报机器人竭诚为您服务，中纪委官网案件查处页面在最近%s小时之内没有发布新的信息。更新时间：%s' % (latest_time, currentDateTime)
    msgTweet = u'#中纪委案件查处 播报机器人竭诚为您服务，中纪委官网案件查处页面在最近%s小时之内没有发布新的信息。更新时间：%s' % (latest_time, currentDateTime)
    broadcast(access_token, post_url, tw_api, msgWeibo, msgTweet)

enable_proxy = False
proxy_handler = urllib2.ProxyHandler({"http" : 'http://192.168.1.1:1111'})
null_proxy_handler = urllib2.ProxyHandler({})
if enable_proxy:
    opener = urllib2.build_opener(proxy_handler)
else:
    opener = urllib2.build_opener(null_proxy_handler)

url = 'http://www.ccdi.gov.cn/ajcc/index'
configFilePath = '/home/duporg/ccdiajcc/config.ini'
urlandtxtInXHourFilePath = '/home/duporg/ccdiajcc/urlandtxtInXHour.txt'
latestUrlsFilePath = '/home/duporg/ccdiajcc/latestUrls.txt'
autoIncreaseFilePath = '/home/duporg/ccdiajcc/autoIncrease.txt'

latestUrlsFile = open(latestUrlsFilePath)
allLines = latestUrlsFile.readlines()
latestUrlsFile.close()
latestUrls = []
for eachLine in allLines:
    latestUrls.append(eachLine.strip('\n').strip())

access_token = '2.004LDAhF0JSg1w8dffa4aa7007f9HL'
post_url = 'https://api.weibo.com/2/statuses/update.json'

tw_api = twitter.Api(consumer_key='ZREdI352yKAFJinjuayECv1YV',
                     consumer_secret='tafphJKVHvFtjhqK9Rk6e8jsvepePLKFjDjw9mP0dfyu053rKv',
                     access_token_key='2647994180-FcTcDnYbO52V8fAMBnkTbkKhWOTpMss80HghT2O',
                     access_token_secret='Jot4sy1rvire4BeAEwK2vjl8cN8KlujUmTIPPrQfP9L7j')

cf = ConfigParser.ConfigParser()
cf.read(configFilePath)
scan_day = cf.getint('scan', 'day')
endDate = int(time.strftime('%Y%m%d',time.gmtime(time.time()+8*60*60-scan_day*24*60*60))) #先算到东八区时间然后往前退X天，需要检查X天之内的所有url
stick_count = cf.getint('stick', 'count') #取得目前有多少条置顶的信息

hasAvailableLi = True
hasValueInUrlandtxtList = False
urlandtxtList = []
newUrlandtxtList = []
page = 1
stickIndex = 0

try:
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
        postDateStartIndex = liStr2.find('<span>')
        postDateEndIndex = liStr2.find('</span>')
        linkUrl = str('http://www.ccdi.gov.cn/ajcc' + liStr[linkUrlStartIndex+10:linkUrlEndIndex-2])
        linkTxt = liStr2[linkTxtStartIndex+2:linkTxtEndIndex]
        postDate = liStr2[postDateStartIndex+6:postDateEndIndex]
        postDate = int(postDate[0:4]+postDate[5:7]+postDate[8:10])
        if stickIndex < stick_count: # 对置顶的信息处理时不比较发布日期
            urlandtxtList.append((linkUrl, linkTxt))
            hasValueInUrlandtxtList = True
            ulStr = ulStr[liEndIndex+5:]
            stickIndex = stickIndex + 1 
        elif postDate > endDate:
            urlandtxtList.append((linkUrl, linkTxt))
            hasValueInUrlandtxtList = True
            ulStr = ulStr[liEndIndex+5:]
        elif postDate < endDate and hasValueInUrlandtxtList == False: #当超过X天没有新的url时
            hasAvailableLi = False
        elif hasValueInUrlandtxtList == True:
            latestUrlsFile = open(latestUrlsFilePath, 'w')
            for urlandtxtItem in urlandtxtList:
                latestUrlsFile.write(urlandtxtItem[0]+'\n')
            latestUrlsFile.close()
            for urlandtxtItem in urlandtxtList:
                existingFlag = False
                for latestUrl in latestUrls:
                    if urlandtxtItem[0] == latestUrl:
                        latestUrls.remove(latestUrl)
                        existingFlag = True
                        break
                if existingFlag == False:
                    newUrlandtxtList.append(urlandtxtItem)
            hasAvailableLi = False
        else: #当X天之内（含X天）没有新的url时
            hasAvailableLi = False

    if len(newUrlandtxtList) != 0:
        for (urlItem,txtItem) in (newUrlandtxtList):
            try:
                timeStr = time.strftime('%Y-%m-%d %H:%M',time.gmtime(time.time()+8*60*60)) #东八区
                msgWeibo = u'%s，来源：%s，更新时间：%s #中纪委案件查处# 温馨提示：万一您发现链接打不开，说明该网页已被编辑撤下。' % (txtItem, urlItem, timeStr)
                msgTweet = u'%s，来源：%s，更新时间：%s #中纪委案件查处 温馨提示：万一您发现链接打不开，说明该网页已被编辑撤下。' % (txtItem, urlItem, timeStr)
                broadcast(access_token, post_url, tw_api, msgWeibo, msgTweet)

                #每次发新信息时，把新信息包括日期小时存入文件里
                ymdhStr = time.strftime('%Y%m%d%H',time.gmtime(time.time()+8*60*60)) #东八区
                ymdhUrlTxt = ymdhStr + ',' + urlItem + ',' + txtItem
                ymdhUrlTxtUnicode = u'%s' % ymdhUrlTxt
                urlandtxtInXHourFile = open(urlandtxtInXHourFilePath, 'a')
                urlandtxtInXHourFile.write(ymdhUrlTxtUnicode.encode('utf-8') +'\n')
                urlandtxtInXHourFile.close()
            except StandardError:
                pass

            time.sleep(5)
except StandardError:
    pass

currentHM = time.strftime('%H%M',time.gmtime(time.time()+8*60*60)) #取得当前时间的小时分钟数
interval_time = cf.getint('interval', 'hour')
start_clock = cf.getint('interval', 'start')
latest_time = cf.getint('latest', 'hour')

start_clock_str = str(start_clock)
if len(start_clock_str) == 1:
    start_clock_str = '0' + start_clock_str
#if re.search(r'^000[0-4]$', currentHM) or re.search(r'^[0-4]$', str(int(currentHM) % (interval_time * 100))): #控制间隔播报时间，由于可能前面程序运行时间超过1分钟，所以除了要判断00分外，还要判断01、02、03、04分
if (start_clock_str == currentHM[0:2] and re.search(r'^0[0-4]$', currentHM[2:4])) or re.search(r'^[0-4]$', str((int(currentHM) - start_clock * 100) % (interval_time * 100))): #控制间隔播报时间，每天从start_clock开始第一次播报，由于可能前面程序运行时间超过1分钟，所以除了要判断00分外，还要判断01、02、03、04分
    urlandtxtInXHourFile = open(urlandtxtInXHourFilePath)
    allLines = urlandtxtInXHourFile.readlines()
    urlandtxtInXHourFile.close()
    if len(allLines) != 0:
        latestDateHour = int(time.strftime('%Y%m%d%H',time.gmtime(time.time()+8*60*60-latest_time*60*60))) #算得需要滚动播报的时间
        urlandtxtInXHourList = []
        newUrlandtxtInXHourList = []
        #读出文件里所有的行存入一个List
        for eachLine in allLines:
            urlandtxtInXHourList.append(eachLine.strip('\n').strip())
        #把X小时之内的信息存在新的List里
        for urlandtxtInXHourItem in urlandtxtInXHourList:
            if latestDateHour <= int(urlandtxtInXHourItem[0:10]):
                newUrlandtxtInXHourList.append(urlandtxtInXHourItem)
        #把X小时之内的信息先写入文件中然后发出去
        if len(newUrlandtxtInXHourList) == 0:
            urlandtxtInXHourFile = open(urlandtxtInXHourFilePath, 'w')
            urlandtxtInXHourFile.truncate()
            urlandtxtInXHourFile.close()
        else:
            urlandtxtInXHourFile = open(urlandtxtInXHourFilePath, 'w')
            for newUrlandtxtInXHourItem in newUrlandtxtInXHourList:
                urlandtxtInXHourFile.write(newUrlandtxtInXHourItem +'\n')
            urlandtxtInXHourFile.close()

            for newUrlandtxtInXHourItem in newUrlandtxtInXHourList:
                try:
                    autoIncreaseFile = open(autoIncreaseFilePath)
                    index = int(autoIncreaseFile.readline().strip('\n').strip())
                    autoIncreaseFile.close()

                    ymdhUrlTxtList = newUrlandtxtInXHourItem.split(',')
                    msgWeibo = u'【%s小时滚动播报】%s，来源：%s #中纪委案件查处# 温馨提示：万一您发现链接打不开，说明该网页已被编辑撤下。' % (latest_time, ymdhUrlTxtList[2].decode('utf-8'), ymdhUrlTxtList[1].decode('utf-8'))
                    msgTweet = u'【%s小时滚动播报】%s，来源：%s #中纪委案件查处 温馨提示：万一您发现链接打不开，说明该网页已被编辑撤下。%s' % (latest_time, ymdhUrlTxtList[2].decode('utf-8'), ymdhUrlTxtList[1].decode('utf-8'), index)
                    broadcast(access_token, post_url, tw_api, msgWeibo, msgTweet)

                    index = index + 1
                    autoIncreaseFile = open(autoIncreaseFilePath, 'w')
                    autoIncreaseFile.write(str(index))
                    autoIncreaseFile.close()
                except StandardError:
                    pass

                time.sleep(5)

if re.search(r'^030[0-4]$', currentHM) or re.search(r'^090[0-4]$', currentHM) or re.search(r'^150[0-4]$', currentHM) or re.search(r'^210[0-4]$', currentHM): #6小时刷一次存在感，报一次心跳，表示还活着
    urlandtxtInXHourFile = open(urlandtxtInXHourFilePath)
    allLines = urlandtxtInXHourFile.readlines()
    urlandtxtInXHourFile.close()
    if len(allLines) == 0:
        heartbeat(latest_time, access_token, post_url, tw_api)
    else:
        latestDateHour = int(time.strftime('%Y%m%d%H',time.gmtime(time.time()+8*60*60-latest_time*60*60)))
        #判断是否有X小时之内的信息，如果没有，心跳一次
        needHeartbeat = True
        for eachLine in allLines:
            if latestDateHour <= int(eachLine.strip('\n').strip()[0:10]):
                needHeartbeat = False
                break
        if needHeartbeat:
            heartbeat(latest_time, access_token, post_url, tw_api)

print time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))
