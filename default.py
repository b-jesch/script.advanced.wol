# Wake-On-LAN

from resources.lib import ping
import os
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
version = addon.getAddonInfo('version')
addon_path = xbmcvfs.translatePath(addon.getAddonInfo('path'))
language = addon.getLocalizedString


def log(message, level=xbmc.LOGDEBUG):
    xbmc.log('[{} {}]: {}'.format(addon_id, version, message), level)


def notify(message, icon, ntime=3000):
    xbmcgui.Dialog().notification(addon_name, message, icon, time=ntime)


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


def main(autostart=False):

    log('Starting WOL script', level=xbmc.LOGINFO)

    # notification settings
    enableLaunchNotifies = True if addon.getSetting("enableLaunchNotifies").lower() == 'true' else False
    enablePingCounterNotifies = True if addon.getSetting("enablePingCounterNotifies").lower() == 'true' else False
    enableHostupNotifies = True if addon.getSetting("enableHostupNotifies").lower() == 'true' else False
    delayHostupNotifies = int(addon.getSetting("delayHostupNotifies"))

    # advanced settings
    pingTimeout = int(addon.getSetting("pingTimeout"))
    hostupWaitTime = int(addon.getSetting("hostupWaitTime"))
    disablePingHostupCheck = True if addon.getSetting("disablePingHostupCheck").lower() == 'true' else False
    updateVideoLibraryAfterWol = True if addon.getSetting("updateVideoLibraryAfterWol").lower() == 'true' else False
    updateMusicLibraryAfterWol = True if addon.getSetting("updateMusicLibraryAfterWol").lower() == 'true' else False
    libraryUpdatesDelay = int(addon.getSetting("libraryUpdatesDelay"))

    # Set Icons
    iconConnect = os.path.join(addon_path, 'resources', 'icons', 'server.png')
    iconError = os.path.join(addon_path, 'resources', 'icons', 'server_error.png')
    iconSuccess = os.path.join(addon_path, 'resources', 'icons', 'server_connect.png')

    # Send WOL-Packets to devices, built devicelist
    dev_list = list()
    for dev in range(4):
        if addon.getSetting('enabled_%s' % dev).lower() == 'true':
            dev_list.append(dev)
            xbmc.executebuiltin('WakeOnLan("%s")' % addon.getSetting('macAddress_%s' % dev))
            log('WakeOnLan signal sent to MAC-Address {}'.format(addon.getSetting('macAddress_%s' % dev)))

            # Send Connection Notification
            if enableLaunchNotifies: notify(language(32400) % (addon.getSetting('hostOrIp_%s' % dev)), iconConnect)
            xbmc.sleep(3000)

    if disablePingHostupCheck:
        # with this setting, we just wait for "hostupWaitTime" seconds and assume a successful wakeup then.
        timecount = 1

        dbg = DialogBG(language(32401),
                       language(32402) % (timecount, hostupWaitTime), enablePingCounterNotifies)
        while timecount <= hostupWaitTime:
            xbmc.sleep(1000)
            dbg.bg_progress(timecount * 100 // hostupWaitTime, language(32402) % (timecount, hostupWaitTime))
            timecount = timecount + 1
        dbg.bg_close()

        if enableHostupNotifies:
            notify(language(32411), iconSuccess)
    else:

        # otherwise we determine the success by pinging (default behaviour)
        timecount = int(time.time())
        dbg = DialogBG(language(32401),
                       language(32402) % (int(time.time()) - timecount, pingTimeout), enablePingCounterNotifies)

        while len(dev_list) > 0 and int(time.time()) - timecount < pingTimeout:

            while int(time.time()) - timecount <= pingTimeout:
                for dev in dev_list:
                    if ping.ping_ip(addon.getSetting('hostOrIp_%s' % dev)):
                        log('last ping successful, %s needed %d secs' % (addon.getSetting('hostOrIp_%s' % dev),
                                                                         (int(time.time()) - timecount)))
                        notify(language(32404) % addon.getSetting('hostOrIp_%s' % dev), iconSuccess)
                        dev_list.remove(dev)
                        xbmc.sleep(3000)

                if len(dev_list) == 0: break
                dbg.bg_progress((int(time.time()) - timecount) * 100 // pingTimeout,
                                language(32402) % (int(time.time()) - timecount, pingTimeout))
                xbmc.sleep(1000)

        dbg.bg_close()

        if delayHostupNotifies > 0:
            log('delay wake up notification for %d secs' % delayHostupNotifies)
            timecount = int(time.time())
            dbg = DialogBG(language(32323),
                           language(32402) % (int(time.time()) - timecount, delayHostupNotifies), True)
            while int(time.time()) - timecount < delayHostupNotifies:
                dbg.bg_progress((int(time.time()) - timecount) * 100 // delayHostupNotifies,
                                language(32402) % (int(time.time()) - timecount, delayHostupNotifies))
                xbmc.sleep(1000)
            dbg.bg_close()

            # notify of unsuccessable wakeups
            devices = list()
            for dev in dev_list: devices.append(addon.getSetting('hostOrIp_%s' % dev))
            if len(devices) > 1: notify(language(32403) % (', '.join(devices)), iconError)
            elif len(devices) == 1: notify(language(32405) % (', '.join(devices)), iconError)
            else: notify(language(32411), iconSuccess)

    # Things to perform after successful wake-up

    # Initiate XBMC-library-updates, if we are in autostart and it is set in the addon.
    if autostart:

        if (updateVideoLibraryAfterWol or updateMusicLibraryAfterWol) and (
                libraryUpdatesDelay > 0):
            xbmc.sleep(libraryUpdatesDelay * 1000)

        if updateVideoLibraryAfterWol:
            log('Initiating Video Library Update')
            xbmc.executebuiltin('UpdateLibrary("video")')

        if updateMusicLibraryAfterWol:
            log('Initiating Music Library Update')
            xbmc.executebuiltin('UpdateLibrary("music")')

    log('Closing WOL script', xbmc.LOGINFO)
    return


if __name__ == '__main__':
    main(autostart=False)
