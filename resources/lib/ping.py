import subprocess
import platform


def ping_ip(current_ip, timeout=1):
    count = 'c'
    wait = ''
    if platform.system().lower() == 'windows':
        count = 'n'
        wait = '-w 1000'
    try:
        subprocess.run("ping -{} 1 {} {}".format(count, wait, current_ip),
                       shell=True, check=True, timeout=timeout)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Ping returns an error: {e}")
        return False


if __name__ == '__main__':
    dns_ips = ['8.8.8.8', '8.8.4.4', '1.2.3.4']
    for ip in dns_ips:
        if ping_ip(ip):
            print(f"{ip} is available")
        else:
            print(f"{ip} is not available")
