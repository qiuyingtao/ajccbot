# coding=utf-8

import urllib
import urllib2
import time
import twitter

enable_proxy = False
proxy_handler = urllib2.ProxyHandler({"http" : 'http://192.168.1.1:1111'})
null_proxy_handler = urllib2.ProxyHandler({})
if enable_proxy:
    opener = urllib2.build_opener(proxy_handler)
else:
    opener = urllib2.build_opener(null_proxy_handler)

url = 'http://www.ccdi.gov.cn/ajcc/index'
urlandtxtIn24hFilePath = '/home/duporg/ccdiajcc/urlandtxtIn24h.txt'
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

endDate = int(time.strftime('%Y%m%d',time.gmtime(time.time()+8*60*60-48*60*60))) #先算到东八区时间然后往前退两天，需要检查两天之内的所有url
hasAvailableLi = True
hasValueInUrlandtxtList = False
urlandtxtList = []
newUrlandtxtList = []
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
    postDateStartIndex = liStr2.find('<span>')
    postDateEndIndex = liStr2.find('</span>')
    linkUrl = str('http://www.ccdi.gov.cn/ajcc' + liStr[linkUrlStartIndex+10:linkUrlEndIndex-2])
    linkTxt = liStr2[linkTxtStartIndex+2:linkTxtEndIndex]
    postDate = liStr2[postDateStartIndex+6:postDateEndIndex]
    postDate = int(postDate[0:4]+postDate[5:7]+postDate[8:10])
    if postDate > endDate:
        urlandtxtList.append((linkUrl, linkTxt))
        hasValueInUrlandtxtList = True
        ulStr = ulStr[liEndIndex+5:]
    elif postDate < endDate and hasValueInUrlandtxtList == False: #当超过两天没有新的url时
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
    else: #当两天之内（含两天）没有新的url时
        hasAvailableLi = False

if len(newUrlandtxtList) != 0:
    urlandtxtIn24hFile = open(urlandtxtIn24hFilePath, 'a')
    for (urlItem,txtItem) in (newUrlandtxtList):
        timeStr = time.strftime('%Y-%m-%d %H:%M',time.gmtime(time.time()+8*60*60)) #东八区
        msgWeibo = u'%s，来源：%s，更新时间：%s #中纪委案件查处#' % (txtItem, urlItem, timeStr)
        msgTweet = u'%s，来源：%s，更新时间：%s #中纪委案件查处' % (txtItem, urlItem, timeStr)

        post_data = urllib.urlencode({'access_token' : access_token, 'status' : msgWeibo.encode('utf-8')})
        r = urllib2.urlopen(post_url, post_data)
        print r.read()

        results = tw_api.PostUpdate(msgTweet.encode('utf-8'))
        print results

        #每次发新信息时，把新信息包括日期小时存入文件里
        ymdhStr = time.strftime('%Y%m%d%H',time.gmtime(time.time()+8*60*60)) #东八区
        ymdhUrlTxt = ymdhStr + ',' + urlItem + ',' + txtItem
        ymdhUrlTxtUnicode = u'%s' % ymdhUrlTxt
        urlandtxtIn24hFile.write(ymdhUrlTxtUnicode.encode('utf-8') +'\n')
        time.sleep(5)
    urlandtxtIn24hFile.close()

last24hDateHM = int(time.strftime('%Y%m%d%H%M',time.gmtime(time.time()+8*60*60-24*60*60))) #算得最近24小时的时间
if last24hDateHM % 200 == 0: #控制每两小时的整点才播报
    last24hDateH = last24hDateHM / 100 #取得日期小时的值
    urlandtxtIn24hFile = open(urlandtxtIn24hFilePath)
    allLines = urlandtxtIn24hFile.readlines()
    urlandtxtIn24hFile.close()
    if len(allLines) != 0:
        urlandtxtIn24hList = []
        newUrlandtxtIn24hList = []
        #读出文件里所有的行存入一个List
        for eachLine in allLines:
            urlandtxtIn24hList.append(eachLine.strip('\n').strip())
        #把24小时之内的信息存在新的List里
        for urlandtxtIn24hItem in urlandtxtIn24hList:
            if last24hDateH <= int(urlandtxtIn24hItem[0:10]):
                newUrlandtxtIn24hList.append(urlandtxtIn24hItem)
        #把24小时之内的信息发出去，并写入文件中
        urlandtxtIn24hFile = open(urlandtxtIn24hFilePath, 'w')
        if len(newUrlandtxtIn24hList) == 0:
            urlandtxtIn24hFile.truncate()
        else:
            autoIncreaseFile = open(autoIncreaseFilePath)
            index = int(autoIncreaseFile.readline().strip('\n').strip())
	    autoIncreaseFile.close()
            autoIncreaseFile = open(autoIncreaseFilePath, 'w')
            for newUrlandtxtIn24hItem in newUrlandtxtIn24hList:
                ymdhUrlTxtList = newUrlandtxtIn24hItem.split(',')
                msgWeibo = u'【24小时滚动播报】%s，来源：%s #中纪委案件查处#' % (ymdhUrlTxtList[2].decode('utf-8'), ymdhUrlTxtList[1].decode('utf-8'))
                msgTweet = u'【24小时滚动播报】%s，来源：%s #中纪委案件查处 %s' % (ymdhUrlTxtList[2].decode('utf-8'), ymdhUrlTxtList[1].decode('utf-8'), str(index))

                post_data = urllib.urlencode({'access_token' : access_token, 'status' : msgWeibo.encode('utf-8')})
                r = urllib2.urlopen(post_url, post_data)
                print r.read()

                results = tw_api.PostUpdate(msgTweet.encode('utf-8'))
                print results

                urlandtxtIn24hFile.write(newUrlandtxtIn24hItem +'\n')
                index = index + 1
                time.sleep(5)
            autoIncreaseFile.write(str(index))
            autoIncreaseFile.close()
        urlandtxtIn24hFile.close()

print time.strftime('%Y-%m-%d %A %X %Z',time.localtime(time.time()))
