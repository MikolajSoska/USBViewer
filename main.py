from usb_viewer import WindowsViewer


def main():
    viewer = WindowsViewer()
    devices = viewer.get_usb_devices()
    for device in devices:
        print(device)


if __name__ == '__main__':
    main()
