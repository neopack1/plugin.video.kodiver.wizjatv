import ast
import threading
import urllib
from datetime import datetime

import xbmc
import xbmcgui
import xbmcplugin

import wizjatv
from shared import *

try:
    import StorageServer
except Exception:
    import storageserverdummy as StorageServer

xbmcplugin.setContent(ADDON_HANDLE, 'movies')


def build_url(params):
    return ADDON_URL + '?' + urllib.urlencode(params)


action = ADDON_ARGS.get('action', None)


def list_item(channel, url):
    li = xbmcgui.ListItem(channel['title'], path=url)
    li.setInfo(type="video", infoLabels={"Title": channel['title']})
    return li


def refresh_epg():
    cache = StorageServer.StorageServer(ADDON_NAME, 24)
    cache.table_name = ADDON_NAME
    timer_inline = threading.Timer(15.0, refresh_epg)

    try:
        from_cache = cache.get("lastEpgRefresh")
        last_refresh = datetime.strptime(from_cache, "%Y-%m-%d %H:%M:%S.%f")
    except TypeError:  # Python, why??
        import time
        last_refresh = datetime.fromtimestamp(time.mktime(time.strptime(from_cache, "%Y-%m-%d %H:%M:%S.%f")))
    except Exception as ex:
        logger.log_err("Cannot read from cache %s" % ex)
        last_refresh = None

    now = datetime.now()
    logger.log_debug("Time of last EPG refresh: %s" % last_refresh)

    if last_refresh is None or (now - last_refresh).total_seconds() > 15 * 60:
        logger.log_notice("Refreshing EPG.")
        xbmc.executebuiltin('Container.Refresh')
        now_as_string = datetime.strftime(now, "%Y-%m-%d %H:%M:%S.%f")
        cache.delete("lastEpgRefresh")
        cache.set("lastEpgRefresh", now_as_string)
    else:
        timer_inline.start()


if action is None:

    channels = wizjatv.list_channels()

    for channel in channels:
        li = xbmcgui.ListItem(channel['title'], iconImage=channel['thumb'], thumbnailImage=channel['thumb'])
        li.setProperty('IsPlayable', 'true')
        li.setProperty('fanart_image', ADDON.getAddonInfo('fanart'))
        li.setInfo(type='video', infoLabels={'plot': channel['epg']})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=build_url({'action': 'play', 'channel': channel}),
                                    listitem=li,
                                    totalItems=len(channels))

    xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

    refresh_epg()

elif action[0] == 'play':

    channel = ast.literal_eval(ADDON_ARGS.get('channel', None)[0])

    logger.log_notice(channel)

    if ADDON.getSetting('plugin.video.kodiver.wizjatv.user') == '':
        ok = xbmcgui.Dialog().ok("No user/pass set for WizjaTV",
                                 "You'll be redirected to settings page to set user/pass", "for WizjaTV.")
        ADDON.openSettings()

    url = wizjatv.channel_stream(channel['id'])

    logger.log_notice("Url to play: %s" % url)
    playItem = list_item(channel, url)
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, playItem)
