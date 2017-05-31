import requests
import xbmc

from bs4 import BeautifulSoup

WIZJA_TV_URL = 'https://wizja.tv/'


def list_channels():
    channels = []
    r = requests.get(WIZJA_TV_URL)
    r.encoding = 'utf-8'
    page = BeautifulSoup(r.text, 'html.parser')
    html_channels = page.find_all('div')[1]
    xbmc.log(str(html_channels), xbmc.LOGERROR)

    for channel in html_channels.find_all("a"):
        xbmc.log(str(channel), xbmc.LOGERROR)
        image_source = str(channel.find_all('img')[0]['src'])
        channels.append({
            'id': str(channel['href']).replace('watch.php?id=', ''),
            'thumb': WIZJA_TV_URL + image_source,
            'title': image_source.replace('ch_logo/', '').replace('.png', '').upper()
        })

    xbmc.log(str(channels), xbmc.LOGERROR)

    return channels
