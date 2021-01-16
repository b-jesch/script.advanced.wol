# Wake-On-LAN

import xbmc
import xbmcaddon
import time

# Read Settings

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
version = addon.getAddonInfo('version')

autostart = addon.getSetting("autostart")
wolAfterStandby = addon.getSetting("wolAfterStandby")
wolDelayOnLaunch = int(addon.getSetting("wolDelayOnLaunch"))
wolDelayAfterStandby = int(addon.getSetting("wolDelayAfterStandby")) * 1000

if autostart.lower() == "true":
    import default

    if wolDelayOnLaunch > 0:
        xbmc.sleep(wolDelayOnLaunch)
    default.main(True)
    if wolAfterStandby.lower() == "true":
        xbmc.log('[{} {}]: Waiting for resume from standby'.format(addon_id, version), xbmc.LOGDEBUG)
        previousTime = int(time.time())
        while not xbmc.Monitor().abortRequested:
            elapsedTime = int(time.time()) - previousTime
            if elapsedTime > 5:
                if wolDelayAfterStandby > 0:
                    xbmc.sleep(wolDelayAfterStandby)
                xbmc.log('[{} {}]: Start WOL script after return '
                         'from standby (took {} secs)'.format(addon_id,
                                                              version,
                                                              int(time.time() - previousTime)),
                         xbmc.LOGDEBUG)

                default.main(True)
                xbmc.log('[{} {}]: Waiting for resume from standby'.format(addon_id, version))
                previousTime = int(time.time())
                xbmc.sleep(1000)
            else:
                previousTime = int(time.time())
                xbmc.sleep(1000)
