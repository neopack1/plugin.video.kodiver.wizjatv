import xbmcaddon

import sys
import urlparse
from utils import ContextAwareLogger

ADDON_NAME = 'plugin.video.kodiver.wizjatv'
ADDON = xbmcaddon.Addon(id=ADDON_NAME)
ADDON_URL = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
ADDON_ARGS = urlparse.parse_qs(sys.argv[2][1:])

logger = ContextAwareLogger(ADDON_NAME)
