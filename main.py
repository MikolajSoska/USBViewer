from viewer.windows import WindowsViewer


def main():
    viewer = WindowsViewer()
    print('Getting USB devices saved in system...')
    devices = viewer.get_usb_devices()
    print('Detected devices:')
    for device in devices:
        print(device.get_details())


if __name__ == '__main__':
    main()
