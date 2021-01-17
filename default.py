# Wake-On-LAN

from resources.lib import ping
import os
import sys
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')


def main(is_autostart=False):
    xbmc.log('[{} {}]: Starting WOL script'.format(addon_id, version), xbmc.LOGDEBUG)

    # Read Settings
    language = addon.getLocalizedString
    notify = xbmcgui.Dialog().notification

    # basic settings
    macAddress = addon.getSetting("macAddress")
    hostOrIp = addon.getSetting("hostOrIp")

    # notification settings
    enableLaunchNotifies = addon.getSetting("enableLaunchNotifies")
    enablePingCounterNotifies = addon.getSetting("enablePingCounterNotifies")
    enableHostupNotifies = addon.getSetting("enableHostupNotifies")

    # advanced settings
    pingTimeout = int(addon.getSetting("pingTimeout"))
    hostupWaitTime = int(addon.getSetting("hostupWaitTime"))
    disablePingHostupCheck = addon.getSetting("disablePingHostupCheck")
    continuousWol = addon.getSetting("continuousWol")
    continuousWolDelay = int(addon.getSetting("continuousWolDelay"))
    continuousWolAfterStandby = addon.getSetting("continuousWolAfterStandby")
    updateVideoLibraryAfterWol = addon.getSetting("updateVideoLibraryAfterWol")
    updateMusicLibraryAfterWol = addon.getSetting("updateMusicLibraryAfterWol")
    libraryUpdatesDelay = int(addon.getSetting("libraryUpdatesDelay"))

    # if the script was called with a 3rd parameter,
    # use the mac-address and host/ip from there

    try:
        if len(sys.argv[3]) > 0:
            arrCustomServer = sys.argv[3].split('@')
            hostOrIp = arrCustomServer[0]
            macAddress = arrCustomServer[1]
    except IndexError:
        pass

    # Set Icons
    iconDir = os.path.join(xbmcvfs.translatePath(addon.getAddonInfo('path')), 'resources', 'icons')
    iconConnect = os.path.join(iconDir, 'server.png')
    iconError = os.path.join(iconDir, 'server_error.png')
    iconSuccess = os.path.join(iconDir, 'server_connect.png')

    launchcommand = False
    delaycommand = False

    try:
        if len(sys.argv[1]) > 0:
            launchcommand = True
            if str(sys.argv[2]) == 'True':
                delaycommand = True
    except:
        pass

    # Launch additional command passed with parameters, if it should not be delayed to after successful wakeup
    if launchcommand and not delaycommand:
        xbmc.executebuiltin(sys.argv[1])

    # Send WOL-Packet
    xbmc.executebuiltin('WakeOnLan("%s")' % macAddress)
    xbmc.log('[{} {}]: WakeOnLan signal sent to MAC-Address {}'.format(addon_id, version, macAddress), xbmc.LOGDEBUG)

    # Send Connection Notification
    if enableLaunchNotifies == "true":
        notify(addon_name, language(60000) % hostOrIp, time=3000, icon=iconConnect)
        xbmc.sleep(3000)

    # Determine wakeup-success
    hostupConfirmed = False
    if disablePingHostupCheck == "true":
        # with this setting, we just wait for "hostupWaitTime" seconds and assume a successful wakeup then.
        timecount = 1

        dbg = xbmcgui.DialogProgressBG()
        dbg.create(language(60001) % hostOrIp, language(60002) % (timecount, hostupWaitTime))
        while timecount <= hostupWaitTime:
            xbmc.sleep(1000)
            if enablePingCounterNotifies == "true":
                dbg.update(timecount * 100 // hostupWaitTime, language(60001) % hostOrIp,
                           language(60002) % (timecount, hostupWaitTime))
            timecount = timecount + 1
        dbg.close()

        if enableHostupNotifies == "true":
            notify(addon_name, language(60011) % hostOrIp, icon=iconSuccess)

        hostupConfirmed = True
    else:
        # otherwise we determine the success by pinging (default behaviour)
        success = False
        timecount = int(time.time())
        now = timecount

        dbg = xbmcgui.DialogProgressBG()
        dbg.create(language(60001) % hostOrIp, language(60002) % (now - timecount, pingTimeout))
        while now - timecount <= pingTimeout:
            success = ping.ping_ip(hostOrIp)
            if not success:
                if enablePingCounterNotifies == "true":
                    dbg.update((now - timecount) * 100 // pingTimeout, language(60001) % hostOrIp,
                               language(60002) % (now - timecount, hostupWaitTime))
                now = int(time.time())
            else:
                break
        dbg.close()

        if not success:
            if enableHostupNotifies == "true":
                notify(addon_name, language(60003) % hostOrIp, icon=iconError)
        else:
            if enableHostupNotifies == "true":
                notify(addon_name, language(60004) % hostOrIp, icon=iconSuccess)
            hostupConfirmed = True

    # Things to perform after successful wake-up
    if hostupConfirmed:

        # Launch additional command passed with parameters, if it should be delayed to after successful wakeup
        if (launchcommand is True) & (delaycommand is True):
            if enableHostupNotifies == "true":
                notify(language(60004) % hostOrIp, language(60007), icon=iconSuccess)
            xbmc.sleep(1000)
            xbmc.executebuiltin(sys.argv[1])

        # Initiate XBMC-library-updates, if we are in autostart and it is set in the addon.
        if is_autostart:

            if ((updateVideoLibraryAfterWol == "true") or (updateMusicLibraryAfterWol == "true")) and (
                    libraryUpdatesDelay > 0):
                xbmc.sleep(libraryUpdatesDelay * 1000)

            if updateVideoLibraryAfterWol == "true":
                xbmc.log('[{} {}]: Initiating Video Library Update'.format(addon_id, version), xbmc.LOGDEBUG)
                xbmc.executebuiltin('UpdateLibrary("video")')

            if updateMusicLibraryAfterWol == "true":
                xbmc.log('[{} {}]: Initiating Music Library Update'.format(addon_id, version), xbmc.LOGDEBUG)
                xbmc.executebuiltin('UpdateLibrary("music")')

    # Continue sending WOL-packets, if configured in the settings
    if continuousWol == "true":
        xbmc.sleep(5000)

        if enableLaunchNotifies == "true":
            # Send Notification regarding continuous WOL-packets
            notify(language(53020), language(60008) % continuousWolDelay, icon=iconSuccess)

        # the previousTime-functionality to stop continuous WOL-packets after XBMC returns from standby was
        # suggested by XBMC-forum-user "jandias" (THANKS!)
        previousTime = int(time.time())
        countingSeconds = 0
        while not xbmc.Monitor().abortRequested():
            if (continuousWolAfterStandby == "false") and (int(time.time()) - previousTime > 5):
                break
            else:
                previousTime = int(time.time())
                xbmc.sleep(1000)
                if countingSeconds == continuousWolDelay:
                    xbmc.executebuiltin('WakeOnLan("%s")' % macAddress)
                    xbmc.log('[{} {}]: WakeOnLan signal sent to MAC-Address {}'.format(addon_id, version, macAddress),
                             xbmc.LOGDEBUG)
                    countingSeconds = 0
                else:
                    countingSeconds += 1

    xbmc.log('[{} {}]: Closing WOL script'.format(addon_id, version), xbmc.LOGDEBUG)
    return


if __name__ == '__main__':
    main()
