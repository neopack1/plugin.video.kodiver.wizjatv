import sys
import urllib
import urlparse

import xbmcaddon
import xbmcgui
import xbmcplugin

import wizjatv

ADDON = xbmcaddon.Addon(id='plugin.video.kodiver.wizjatv')
ADDON_URL = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
ADDON_ARGS = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(ADDON_HANDLE, 'movies')


def build_url(params):
    return ADDON_URL + '?' + urllib.urlencode(params)


action = ADDON_ARGS.get('action', None)

if action is None:
    for item in wizjatv.list_channels():
        li = xbmcgui.ListItem(item['title'], iconImage=item['thumb'], thumbnailImage=item['thumb'])
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url="", listitem=li)
    xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
