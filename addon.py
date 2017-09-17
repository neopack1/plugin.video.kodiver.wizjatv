# -*- coding: utf-8 -*-

import ast
import urllib

import xbmcgui
import xbmcplugin

import wizjatv
from shared import *

xbmcplugin.setContent(ADDON_HANDLE, 'movies')


def build_url(params):
    return ADDON_URL + '?' + urllib.urlencode(params)


action = ADDON_ARGS.get('action', None)


def create_play_item(channel, url):
    li = xbmcgui.ListItem(channel['title'], path=url)
    li.setInfo(type="video", infoLabels={"Title": channel['title']})
    return li


if action is None:

    channels = wizjatv.list_channels()

    for channel in channels:
        li = xbmcgui.ListItem(channel['title'], iconImage=channel['thumb'], thumbnailImage=channel['thumb'])
        li.setProperty('IsPlayable', 'true')
        li.setProperty('fanart_image', ADDON.getAddonInfo('fanart'))
        li.setInfo(type='video', infoLabels={'plot': channel['epg']})
        li.addContextMenuItems([('Odśwież EPG', 'Container.Refresh')])
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=build_url({'action': 'play', 'channel': channel}),
                                    listitem=li,
                                    totalItems=len(channels))

    xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)


elif action[0] == 'play':

    channel = ast.literal_eval(ADDON_ARGS.get('channel', None)[0])

    logger.log_notice(channel)

    if ADDON.getSetting('plugin.video.kodiver.wizjatv.user') == '':
        ok = xbmcgui.Dialog().ok("No user/pass set for WizjaTV",
                                 "You'll be redirected to settings page to set user/pass", "for WizjaTV.")
        ADDON.openSettings()

    url = wizjatv.channel_stream(channel['id'])

    logger.log_notice("Url to play: %s" % url)
    playItem = create_play_item(channel, url)
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, playItem)
