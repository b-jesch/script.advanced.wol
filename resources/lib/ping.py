# script by Dmitry Golovach
# source https://dmitrygolovach.com/python-ping-ip-address/

import subprocess
import platform


def ping_ip(current_ip_address, timeout=1):
    try:
        output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower(
        ) == "windows" else 'c', current_ip_address), shell=True, universal_newlines=True)
        if 'unreachable' in output:
            return False
        else:
            return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    current_ip_address = ['8.8.8.8', '8.8.4.4', '1.2.3.4']
    for each in current_ip_address:
        if ping_ip(each):
            print(f"{each} is available")
        else:
            print(f"{each} is not available")
