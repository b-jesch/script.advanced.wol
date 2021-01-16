# Wake-On-LAN

import socket
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
    enableErrorNotifies = addon.getSetting("enableErrorNotifies")

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
    iconConnect = os.path.join(iconDir, 'server_connect.png')
    iconError = os.path.join(iconDir, 'server_error.png')
    iconSuccess = os.path.join(iconDir, 'server.png')

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
        notify(addon_name, language(60000) % hostOrIp, icon=iconConnect)

    # Determine wakeup-success
    hostupConfirmed = False
    if disablePingHostupCheck == "true":
        # with this setting, we just wait for "hostupWaitTime" seconds and assume a successful wakeup then.
        timecount = 1
        while timecount <= hostupWaitTime:
            xbmc.sleep(1000)
            if enablePingCounterNotifies == "true":
                notify(language(60001) % hostOrIp, language(60002) % (timecount, hostupWaitTime),
                       time=1000, icon=iconConnect)
            timecount = timecount + 1
        if enableHostupNotifies == "true":
            notify(addon_name, language(60011) % hostOrIp, icon=iconSuccess)
        hostupConfirmed = True
    else:
        # otherwise we determine the success by pinging (default behaviour)
        delay = None
        try:
            timecount = 1
            while timecount <= pingTimeout:
                delay = ping.do_one(hostOrIp, 1)
                if delay is None:
                    if enablePingCounterNotifies == "true":
                        notify(language(60001) % hostOrIp, language(60002) % (timecount, pingTimeout),
                               time=1000, icon=iconConnect)
                    timecount = timecount + 1
                else:
                    break
            if delay is None:
                xbmc.sleep(1000)
                if enableHostupNotifies == "true":
                    notify(addon_name, language(60003) % hostOrIp, icon=iconError)
            else:
                xbmc.sleep(1000)
                if enableHostupNotifies == "true":
                    notify(addon_name, language(60004) % hostOrIp, icon=iconSuccess)
                hostupConfirmed = True

        except socket.gaierror as e:
            xbmc.log('[{} {}]: {}'.format(addon_id, version, e), xbmc.LOGERROR)
            notify(language(60005), language(60006) % hostOrIp, time=10000, icon=iconError)
        except PermissionError as e:
            xbmc.log('[{} {}]: {}'.format(addon_id, version, e), xbmc.LOGERROR)
            if enablePingCounterNotifies.lower() == "true":
                if sys.platform == 'win32':
                    notify(language(60005), language(60009), time=20000, icon=iconError)
                elif sys.platform == 'linux2':
                    notify(language(60005), language(60010), time=20000, icon=iconError)
                else:
                    notify(language(60005), str(e), time=20000, icon=iconError)
        except socket.error as e:
            xbmc.log('[{} {}]: {}'.format(addon_id, version, e), xbmc.LOGERROR)
            notify(language(60005), str(e), time=20000, icon=iconError)

    # Things to perform after successful wake-up
    if hostupConfirmed:

        # Launch additional command passed with parameters, if it should be delayed to after successful wakeup
        if (launchcommand == True) & (delaycommand == True):
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
