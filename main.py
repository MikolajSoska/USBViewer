import platform
from typing import Optional

from viewer.base import BaseViewer
from viewer.linux import LinuxViewer
from viewer.windows import WindowsViewer


def get_usb_viewer() -> Optional[BaseViewer]:
    if platform.system() == 'Windows':
        return WindowsViewer()
    elif platform.system() == 'Linux':
        return LinuxViewer()
    else:
        print(f'Script doesn\'t support system: {platform.system()}.')
        return None


def main():
    viewer = get_usb_viewer()
    print('Getting USB devices saved in system...')
    devices = viewer.get_usb_devices()
    print('Detected devices:')
    for device in devices:
        print(device.get_details())


if __name__ == '__main__':
    main()
