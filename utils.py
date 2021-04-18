import gzip
from typing import List, Tuple, Optional, Iterator, IO

import bs4
import requests


def convert_binary_to_ascii_string(binary_string: bytes) -> str:
    return ''.join([chr(byte) for byte in binary_string if 0 < byte < 128])


def convert_windows_time_to_unix(windows_timestamp: int) -> int:
    windows_tick = 10000000
    seconds_to_unix_epoch = 11644473600

    return int(windows_timestamp / windows_tick - seconds_to_unix_epoch)


def parse_windows_log_file(filepath: str) -> Iterator[List[str]]:
    with open(filepath, 'r') as log_file:
        log_section = []
        for line in log_file:

            # Each section starts with two lines with '>>>' at the line beginning
            if len(log_section) == 0 and line.startswith('>>>'):
                next_line = next(log_file)
                if next_line.startswith('>>>'):
                    log_section.append(line)
                    log_section.append(next_line)
                    continue

            # Each section ends with two lines with '<<<' at the line beginning
            if len(log_section) > 0 and line.startswith('<<<'):
                next_line = next(log_file)
                if next_line.startswith('<<<'):
                    log_section.append(line)
                    log_section.append(next_line)

                    yield log_section
                    log_section.clear()
                    continue

            # Adding lines to section
            if len(log_section) > 0:
                log_section.append(line)


def get_device_info_from_web(vendor_id: str, product_id: str, max_attempts: int = 3) -> Tuple[Optional[str],
                                                                                              Optional[str]]:
    if max_attempts <= 0:
        print(f'Unable to retrieve device information from the Web (Vendor ID: {vendor_id}, Product ID: {product_id}).')
        return None, None

    url = f'https://devicehunt.com/view/type/usb/vendor/{vendor_id}/device/{product_id}'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        def get_info_from_section(info_type: str) -> Optional[str]:
            section = soup.find('div', attrs={'class': f'--type-{info_type}'})
            if section is not None:
                return section.find(None, attrs={'class': 'details__heading'}).text.strip()
            else:
                return None

        vendor_name = get_info_from_section('vendor')
        device_description = get_info_from_section('device')

        return vendor_name, device_description

    else:
        return get_device_info_from_web(vendor_id, product_id, max_attempts - 1)


def open_linux_log_file(filepath: str) -> IO:
    if filepath.endswith('.gz'):
        return gzip.open(filepath, 'rt')
    else:
        return open(filepath, 'r')


def parse_linux_log_file(filepath: str) -> Iterator[List[str]]:
    with open_linux_log_file(filepath) as log_file:
        section = []
        for line in log_file:
            if 'New USB device found' in line:
                if len(section) == 0:
                    section.append(line)
                    continue
                else:  # Previous section wasn't USB device
                    section.clear()
                    section.append(line)

            if len(section) > 0 and 'Mounted /dev/sd' in line:
                section.append(line)
                yield section
                section.clear()
