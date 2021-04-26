import os
import urllib
from bs4 import BeautifulSoup
import time
import re

def openUrl(url):
    # 添加try语句
    header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=header)
    respone = urllib.request.urlopen(req)
    content = respone.read()
    return content

def saveDataWithUrl(tags, baseUrl, savePath='./data/'):
    if len(tags) <= 0:
        return
    targetLabel = 'href' if tags[0].get('href') else 'src'
    for tag in tags:
        link = tag.get(targetLabel)
        # 如果不能通过href或src获取到链接，遍历tag的attrs进行正则匹配重新获取
        if not link:
            for key in tag.attrs:
                if re.search(re.compile('href|src'), key):
                    targetLabel = key
                    link = tag.get(targetLabel)
        # print('got link: ', link)
        name = link.split('/')[-1]
        targetUrl = urllib.parse.urljoin(baseUrl, link)
        data = openUrl(targetUrl)
        newlink = savePath + name
        if not os.path.exists(newlink):
            with open(newlink, 'wb') as f:
                f.write(data)
            # print('save data done, path: ', newlink)
        tag[targetLabel] = './resource/' + name

def main(baseUrl, savePath='./'):
    content = openUrl(baseUrl)
    soup = BeautifulSoup(content, 'html.parser')
    filename = baseUrl.split('/')[-1]
    cssTags = soup.find_all('link')
    scriptTags = soup.find_all('script')
    aTags = soup.find_all('a')
    imgTags = soup.find_all(['img', 'image'])
    # url = 'http://www.baidu.com'
    temp = soup.find_all('div', 'reader-to-vip')
    temp[0].decompose()
    resourcePath = savePath + 'resource/'
    isExists = os.path.exists(resourcePath)
    if not isExists:
        os.mkdir(resourcePath)
        print('指定目录下resource不存在，已自行创建')
    saveDataWithUrl(imgTags, baseUrl, resourcePath)
    saveDataWithUrl(cssTags, baseUrl, resourcePath)
    saveDataWithUrl(scriptTags, baseUrl, resourcePath)

    # get button next chapter url
    nextUrl = None
    nextTags = soup.find_all('a', 'a_next')
    if nextTags:
        nextUrl = urllib.parse.urljoin(baseUrl, nextTags[0].get('href'))
    for i in aTags:
        link = i.get('href')
        if not link:
            continue
        link = link.split('#')[0]
        name = link.split('/')[-1]
        i['href'] = './' + name
    with open(savePath + filename, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    return nextUrl

if __name__ == '__main__':
    # baseUrl为封面页
    # baseUrl = 'http://reader.obook.vip/books/mobile/04/042fe331ce51da2f9be70c40aae1b334/titlepage.html'
    baseUrl = 'http://reader.obook.vip/books/mobile/80/8027eef24402a684a177ce69956e1a58/cover1.html'
    savePath = './shangyin/'
    sleepTime = 3
    if not os.path.exists(savePath):
        os.mkdir(savePath)
    nextUrl = main(baseUrl, savePath)
    while(nextUrl):
        print('download next url: ', nextUrl)
        time.sleep(sleepTime)
        nextUrl = main(nextUrl, savePath)
    print('process done!')
    # TODO删除下载到资源中的hm开头的js依赖项
