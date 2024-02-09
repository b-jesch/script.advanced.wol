import xbmc
import xbmcaddon
import time

# Read Settings

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
version = addon.getAddonInfo('version')

autostart = True if addon.getSetting("autostart").lower() == 'true' else False
wolAfterStandby = True if addon.getSetting("wolAfterStandby").lower() == 'true' else False

mon = xbmc.Monitor()
if autostart:

    import default
    wolDelayOnLaunch = int(addon.getSetting("wolDelayOnLaunch"))
    wolDelayAfterStandby = int(addon.getSetting("wolDelayAfterStandby"))

    if wolDelayOnLaunch > 0: xbmc.sleep(wolDelayOnLaunch * 1000)

    default.main(autostart=autostart)

    if wolAfterStandby:
        previousTime = int(time.time())

        while not mon.abortRequested():

            # if elapsedTime > 60 secs possibly there was an inactive state between (standby?)

            if int(time.time()) - previousTime > 60:
                if int(addon.getSetting("wolDelayAfterStandby")) > 0: xbmc.sleep(wolDelayAfterStandby * 1000)

                default.log('Start WOL after standby (sleeped {} secs)'.format(int(time.time() - previousTime)))
                default.main(True)

            previousTime = int(time.time())
            mon.waitForAbort(10)

        default.log('abort requested', xbmc.LOGINFO)
