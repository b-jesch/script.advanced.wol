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


class DialogBG(xbmcgui.DialogProgressBG):
    def __init__(self, heading, message, visible=True):
        super().__init__()

        self.heading = heading
        self.message = message
        self.visible = visible

        if self.visible:
            self.create(heading, message)

    def bg_progress(self, percent, message=None):
        if self.visible:
            if message is not None:
                self.message = message
            self.update(percent, self.heading, self.message)

    def bg_close(self):
        if self.visible:
            self.close()


def main(is_autostart=False):
    xbmc.log('[{} {}]: Starting WOL script'.format(addon_id, version), xbmc.LOGDEBUG)

    # Read Settings
    language = addon.getLocalizedString
    notify = xbmcgui.Dialog().notification

    # basic settings
    macAddress = addon.getSetting("macAddress")
    hostOrIp = addon.getSetting("hostOrIp")

    # notification settings
    enableLaunchNotifies = True if addon.getSetting("enableLaunchNotifies").lower() == 'true' else False
    enablePingCounterNotifies = True if addon.getSetting("enablePingCounterNotifies").lower() == 'true' else False
    enableHostupNotifies = True if addon.getSetting("enableHostupNotifies").lower() == 'true' else False
    delayHostupNotifies = int(addon.getSetting("delayHostupNotifies"))

    # advanced settings
    pingTimeout = int(addon.getSetting("pingTimeout"))
    hostupWaitTime = int(addon.getSetting("hostupWaitTime"))
    disablePingHostupCheck = True if addon.getSetting("disablePingHostupCheck").lower() == 'true' else False
    continuousWol = True if addon.getSetting("continuousWol").lower() == 'true' else False
    continuousWolDelay = int(addon.getSetting("continuousWolDelay"))
    continuousWolAfterStandby = True if addon.getSetting("continuousWolAfterStandby").lower() == 'true' else False
    continuousWolOnlyWhilePlaying = True if addon.getSetting("continuousWolOnlyWhilePlaying").lower() == 'true' else False
    updateVideoLibraryAfterWol = True if addon.getSetting("updateVideoLibraryAfterWol").lower() == 'true' else False
    updateMusicLibraryAfterWol = True if addon.getSetting("updateMusicLibraryAfterWol").lower() == 'true' else False
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
    except IndexError:
        pass

    # Launch additional command passed with parameters, if it should not be delayed to after successful wakeup
    if launchcommand and not delaycommand:
        xbmc.executebuiltin(sys.argv[1])

    # Send WOL-Packet
    xbmc.executebuiltin('WakeOnLan("%s")' % macAddress)
    xbmc.log('[{} {}]: WakeOnLan signal sent to MAC-Address {}'.format(addon_id, version, macAddress), xbmc.LOGDEBUG)

    # Send Connection Notification
    if enableLaunchNotifies:
        notify(addon_name, language(60000) % hostOrIp, time=3000, icon=iconConnect)
        xbmc.sleep(3000)

    # Determine wakeup-success
    hostupConfirmed = False
    if disablePingHostupCheck:
        # with this setting, we just wait for "hostupWaitTime" seconds and assume a successful wakeup then.
        timecount = 1

        dbg = DialogBG(language(60001) % hostOrIp,
                       language(60002) % (timecount, hostupWaitTime), enablePingCounterNotifies)
        while timecount <= hostupWaitTime:
            xbmc.sleep(1000)
            dbg.bg_progress(timecount * 100 // hostupWaitTime, language(60002) % (timecount, hostupWaitTime))
            timecount = timecount + 1
        dbg.bg_close()

        if enableHostupNotifies:
            notify(addon_name, language(60011) % hostOrIp, icon=iconSuccess)

        hostupConfirmed = True
    else:
        # otherwise we determine the success by pinging (default behaviour)
        success = False
        timecount = int(time.time())
        now = timecount

        dbg = DialogBG(language(60001) % hostOrIp,
                       language(60002) % (now - timecount, pingTimeout), enablePingCounterNotifies)
        while now - timecount <= pingTimeout:
            success = ping.ping_ip(hostOrIp)
            if not success:
                now = int(time.time())
                dbg.bg_progress((now - timecount) * 100 // pingTimeout,
                                language(60002) % (now - timecount, pingTimeout))
            else:
                xbmc.log('last ping was successful, {} secs needed'.format(now - timecount), xbmc.LOGDEBUG)
                if delayHostupNotifies > 0:
                    xbmc.log('delay wake up notification for {} secs'.format(delayHostupNotifies), xbmc.LOGDEBUG)
                    steps = delayHostupNotifies
                    while steps >= 0:
                        xbmc.sleep(1000)
                        dbg.bg_progress((delayHostupNotifies - steps) * 100 // delayHostupNotifies,
                                        language(60005) % (delayHostupNotifies - (delayHostupNotifies - steps)))
                        steps -= 1
                hostupConfirmed = True
                break
        dbg.bg_close()

        if enableHostupNotifies:
            if not success:
                notify(addon_name, language(60003) % hostOrIp, icon=iconError)
            else:
                notify(addon_name, language(60004) % hostOrIp, icon=iconSuccess)

    # Things to perform after successful wake-up
    if hostupConfirmed:

        # Launch additional command passed with parameters, if it should be delayed to after successful wakeup
        if launchcommand and delaycommand:
            if enableHostupNotifies:
                notify(language(60004) % hostOrIp, language(60007), icon=iconSuccess)
            xbmc.sleep(1000)
            xbmc.executebuiltin(sys.argv[1])

        # Initiate XBMC-library-updates, if we are in autostart and it is set in the addon.
        if is_autostart:

            if (updateVideoLibraryAfterWol or updateMusicLibraryAfterWol) and (
                    libraryUpdatesDelay > 0):
                xbmc.sleep(libraryUpdatesDelay * 1000)

            if updateVideoLibraryAfterWol:
                xbmc.log('[{} {}]: Initiating Video Library Update'.format(addon_id, version), xbmc.LOGDEBUG)
                xbmc.executebuiltin('UpdateLibrary("video")')

            if updateMusicLibraryAfterWol:
                xbmc.log('[{} {}]: Initiating Music Library Update'.format(addon_id, version), xbmc.LOGDEBUG)
                xbmc.executebuiltin('UpdateLibrary("music")')

    # Continue sending WOL-packets, if configured in the settings
    if continuousWol:
        xbmc.sleep(5000)

        if enableLaunchNotifies:
            # Send Notification regarding continuous WOL-packets
            notify(language(53020), language(60008) % continuousWolDelay, icon=iconSuccess)

        # the previousTime-functionality to stop continuous WOL-packets after XBMC returns from standby was
        # suggested by XBMC-forum-user "jandias" (THANKS!)
        previousTime = int(time.time())
        countingSeconds = 0
        while not xbmc.Monitor().abortRequested():
            if (not continuousWolAfterStandby) and (int(time.time()) - previousTime > 5):
                break
            else:
                previousTime = int(time.time())
                xbmc.sleep(1000)
                if countingSeconds == continuousWolDelay:

                    if (not continuousWolOnlyWhilePlaying) or xbmc.Player().isPlaying():
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
