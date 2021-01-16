
The Addon can be launched manually from the Programs-section of Kodi (and thus added to your favourites, etc.), and can also be configured in the addon-settings to autostart with Kodi, thus waking up your remote device when Kodi starts.
There is also a setting that will also send a wake-up signal, if Kodi comes out from standby/sleep/suspend.

When autostarted with Kodi you can also set the addon to update the video- and/or music-libraries automatically after a successful wake-up.
You can also set up a delay for the library scans. This is needed, if the filesystem needs some further time to get ready after a successful wake-up.

Additionally another command (e.g. activate a specific window) can be handed to the script as a parameter. It then launches that command either immediately or not until the remote device is available. Behaviour can be set by a second parameter:
  - False: launch immediately (default)
  - True: wait for remote device

As an example, you could add the following entry to your favourites.xml:

        RunScript(script.advanced.wol,ActivateWindow(MyVideoLibrary),True)

This would attempt to wake the remote device configured in the Advanced Wake On Lan-Settings, wait until it is awake, and only then launch the Kodi-Video-Library.

This feature is especially useful, if you want to launch your remote device, when entering a specific menu-item in Kodi.

You can also pass the Host/IP and MAC-Address of the remote device to the script as the third parameter, bypassing the config in the addon-settings. E.g.:

        RunScript(script.advanced.wol,,,my-server@50:E5:49:B5:61:34)

In the advanced settings you can also set the addon to continue sending WOL packets with a configurable delay.
This is useful, when the remote device or NAS is kept awake, as long as WOL-packets are received.
Normally the continuous WOL-packets will also continue after Kodi has returned from standby/sleep/suspend, but there is an option to turn this behaviour off.
