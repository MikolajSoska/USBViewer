def convert_binary_to_ascii_string(binary_string: bytes) -> str:
    return ''.join([chr(byte) for byte in binary_string if 0 < byte < 128])


def convert_windows_time_to_unix(windows_timestamp: int) -> int:
    windows_tick = 10000000
    seconds_to_unix_epoch = 11644473600

    return int(windows_timestamp / windows_tick - seconds_to_unix_epoch)
