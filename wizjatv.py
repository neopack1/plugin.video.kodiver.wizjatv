# -*- coding: utf-8 -*-

import re
import urllib
import ast

import requests
from bs4 import BeautifulSoup

from shared import *

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


def wizja_login():
    try:
        params = {}

        params['login'] = 'zaloguj'
        params['user_name'] = ADDON.getSetting('plugin.video.kodiver.wizjatv.user')
        params['user_password'] = ADDON.getSetting('plugin.video.kodiver.wizjatv.pass')

        result = requests.post(WIZJA_TV_LOGIN_URL, data=params)

        cookie = result.cookies.get_dict()

        ADDON.setSetting('plugin.video.kodiver.wizjatv.cookie', str(cookie))

    except Exception as e:
        logger.log_err("%s" % e)
    return


def channel_stream(channel_id):
    if has_cookies():
        cookie = ast.literal_eval(ADDON.getSetting('plugin.video.kodiver.wizjatv.cookie'))
        result = requests.get(WIZJA_TV_LOGIN_URL, cookies=cookie)

        if 'Zalogowany jako' not in result.content:
            logger.log_notice('Cookies set, but not loged in. Login in.')
            wizja_login()
        else:
            logger.log_notice('Cookies set, and loged in.')
    else:
        logger.log_notice('Cookies not set. Login in.')
        wizja_login()

    try:

        cookie = ast.literal_eval(ADDON.getSetting('plugin.video.kodiver.wizjatv.cookie'))

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

        return create_rtmp_from_src(re.compile('src: "(.*?)"').findall(content)[0], ref)

    except Exception as e:
        logger.log_err('%s' % e)
    return


def has_cookies():
    if ADDON.getSetting('plugin.video.kodiver.wizjatv.cookie') == "":
        return False
    else:
        return True


def create_rtmp_from_src(src, ref):
    decoded_rtmp = urllib.unquote(src).decode('utf8')
    rtmp_sections = re.compile('rtmp://(.*?)/(.*?)/(.*?)\?(.*?)\&streamType').findall(decoded_rtmp)
    xbmc_rtmp = 'rtmp://' + rtmp_sections[0][0] + '/' + rtmp_sections[0][1] + '?' + rtmp_sections[0][3] + \
               ' app=' + rtmp_sections[0][1] + '?' + rtmp_sections[0][3] + \
               ' playpath=' + rtmp_sections[0][2] + '?' + rtmp_sections[0][3] + \
               ' swfVfy=1 flashver=LNX\\25,0,0,12 timeout=25 ' \
               'swfUrl=https://wizja.tv/player/StrobeMediaPlayback_v4.swf live=true ' \
               'pageUrl=' + ref
    return xbmc_rtmp
