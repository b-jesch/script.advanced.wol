import xbmc
import xbmcaddon
import time
import re

# Read Settings

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
version = addon.getAddonInfo('version')

autostart = True if addon.getSetting("autostart").lower() == 'true' else False
wolAfterStandby = True if addon.getSetting("wolAfterStandby").lower() == 'true' else False

if autostart:

    import default
    wolDelayOnLaunch = int(re.findall('^[0-9]*', addon.getSetting("wolDelayOnLaunch"))[0])
    wolDelayAfterStandby = int(re.findall('^[0-9]*', addon.getSetting("wolDelayAfterStandby"))[0])

    if wolDelayOnLaunch > 0: xbmc.sleep(wolDelayOnLaunch * 1000)

    default.main(autostart=autostart)

    if wolAfterStandby:
        previousTime = int(time.time())

        while not xbmc.Monitor().abortRequested:
            elapsedTime = int(time.time()) - previousTime

            # if elapsedTime > 60 secs possibly there was an inactive state between (standby?)

            if elapsedTime > 60:
                if int(addon.getSetting("wolDelayAfterStandby")) > 0:
                    xbmc.sleep(wolDelayAfterStandby * 1000)

                default.log('Start WOL after standby (sleeped {} secs)'.format(int(time.time() - previousTime)))
                default.main(True)

            previousTime = int(time.time())
            xbmc.sleep(1000)
