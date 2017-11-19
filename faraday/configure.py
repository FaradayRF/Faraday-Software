import subprocess
import time


def main():
    """Main function"""
    # Start proxy server
    #proxy = subprocess.Popen(["faraday-proxy", "--start"])
    #proxy.communicate()

    time.sleep(2)

    # Start deviceconfiguration server
    #configuration = subprocess.Popen(["faraday-deviceconfiguration", "--start"])
    #configuration.communicate()

    time.sleep(2)

    # Start simpleconfig server
    simpleconfig = subprocess.Popen(["faraday-simpleconfig", "--read", "--start"])
    simpleconfig.communicate()


if __name__ == '__main__':
    main()
