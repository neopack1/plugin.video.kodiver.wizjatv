# -*- coding: utf-8 -*-

import re
import urllib

import requests
import xbmc
import xbmcaddon
from bs4 import BeautifulSoup

WIZJA_TV_URL = 'https://wizja.tv/'
WIZJA_TV_LOGIN_URL = WIZJA_TV_URL + 'users/index.php'
WIZJA_TV_WATCH_URL = WIZJA_TV_URL + 'watch.php'
WIZJA_TV_PORTER_URL = WIZJA_TV_URL + 'porter.php'
WIZJA_TV_KILLME_URL = WIZJA_TV_URL + 'killme.php'


def list_channels():
    channels = []
    r = requests.get(WIZJA_TV_URL)
    r.encoding = 'utf-8'
    page = BeautifulSoup(r.text, 'html.parser')
    html_channels = page.find_all('div')[1]

    for channel in html_channels.find_all("a"):
        image_source = str(channel.find_all('img')[0]['src'])
        channel_id = str(channel['href']).replace('watch.php?id=', '')

        channels.append({
            'id': channel_id,
            'thumb': WIZJA_TV_URL + image_source,
            'title': image_source.replace('ch_logo/', '').replace('.png', '').upper()
        })

    return channels


def wizjalogin():
    try:
        params = {}
        url = WIZJA_TV_LOGIN_URL

        params['login'] = 'zaloguj'
        params['user_name'] = xbmcaddon.Addon(id='plugin.video.kodiver.wizjatv').getSetting(
            'plugin.video.kodiver.wizjatv.user')
        params['user_password'] = xbmcaddon.Addon(id='plugin.video.kodiver.wizjatv').getSetting(
            'plugin.video.kodiver.wizjatv.pass')

        result = requests.post(url, data=params)

        cookie = result.cookies.get_dict()

        xbmcaddon.Addon(id='plugin.video.kodiver.wizjatv').setSetting('plugin.video.kodiver.wizjatv.cookie',
                                                                      str(cookie))

    except Exception as e:
        xbmc.log(e, xbmc.LOGWARNING)
    return


def channelStream(channel_id):
    wizjalogin()

    try:

        cookie = eval(
            xbmcaddon.Addon(id='plugin.video.kodiver.wizjatv').getSetting('plugin.video.kodiver.wizjatv.cookie'))

        ref = WIZJA_TV_WATCH_URL + '?id=%s' % channel_id
        requests.get(ref, cookies=cookie)
        url = WIZJA_TV_PORTER_URL + '?ch=%s' % channel_id

        result = requests.get(url, cookies=cookie, headers={'Referer': ref})
        content = result.content

        if '<a href="killme.php?id' in content:
            requests.get(WIZJA_TV_KILLME_URL + '?id=%s' % channel_id, cookies=cookie, headers={'Referer': ref})

            ref = WIZJA_TV_WATCH_URL + '?id=%s' % channel_id
            requests.get(ref, cookies=cookie, headers={'Referer': ref})
            result = requests.get(url, cookies=cookie, headers={'Referer': ref})
            content = result.content

        return createRtmpFromSrc(re.compile('src: "(.*?)"').findall(content)[0], ref)

    except Exception as e:
        xbmc.log('%s' % e, xbmc.LOGWARNING)
    return


def createRtmpFromSrc(src, ref):
    decodedRtmp = urllib.unquote(src).decode('utf8')
    rtmpSections = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(decodedRtmp)
    xbmcRtmp = 'rtmp://' + rtmpSections[0][0] + '/' + rtmpSections[0][1] + '?' + rtmpSections[0][3] + \
               ' app=' + rtmpSections[0][1] + '?' + rtmpSections[0][3] + \
               ' playpath=' + rtmpSections[0][2] + '?' + rtmpSections[0][3] + \
               ' swfVfy=1 flashver=LNX\\25,0,0,12 timeout=25 ' \
               'swfUrl=https://wizja.tv/player/StrobeMediaPlayback_v4.swf live=true ' \
               'pageUrl=' + ref
    return xbmcRtmp
