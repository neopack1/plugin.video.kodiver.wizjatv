import sys
import urllib
import urlparse

import xbmc
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

    channels = wizjatv.list_channels()
    for channel in channels:
        li = xbmcgui.ListItem(channel['title'], iconImage=channel['thumb'], thumbnailImage=channel['thumb'])
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=build_url({'action': 'play', 'channel': channel['id']}),
                                    listitem=li, totalItems=len(channels))
    xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

elif action[0] == 'play':
    if ADDON.getSetting('plugin.video.kodiver.wizjatv.user') == '':
        ok = xbmcgui.Dialog().ok("No user/pass set for WizjaTV",
                                 "You'll be redirected to settings page to set user/pass", "for WizjaTV.")
        ADDON.openSettings()

    url = wizjatv.channelStream(ADDON_ARGS.get('channel', None)[0])

    xbmc.log(url, xbmc.LOGWARNING)

    try:
        playItem = xbmcgui.ListItem('title', path=url)
        playItem.setInfo(type="video", infoLabels={"Title": "Title"})

        xbmcPlayer = xbmc.Player()
        xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, playItem)

        for i in range(0, 240):
            if xbmcPlayer.isPlayingVideo():
                break
            xbmc.sleep(1000)

    except Exception as e:
        xbmc.log('ERROR PLAY:%s' % e, xbmc.LOGWARNING)
