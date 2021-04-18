# USB Viewer

Program for Computer Forensics course in university. This tool reads history and main information about previously
connected USB devices from system registers/logs.

Script automatically performs operations for detected OS.

### Tested on:

- Windows 10
- Ubuntu

### Installation

- Clone repository
- Run `python setup.py bdist_wheel`
- Install `.whl` file located in `dist` directory

### Running

- if whl is installed: `python -m usb_viewer`
- else: `python usb_viewer.__main__`
