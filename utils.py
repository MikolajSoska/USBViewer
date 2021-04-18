def convert_binary_to_ascii_string(binary_string: bytes) -> str:
    return ''.join([chr(byte) for byte in binary_string if 0 < byte < 128])


def convert_windows_time_to_unix(windows_timestamp: int) -> int:
    windows_tick = 10000000
    seconds_to_unix_epoch = 11644473600

    return int(windows_timestamp / windows_tick - seconds_to_unix_epoch)


def parse_windows_log_file(filepath: str):
    with open(filepath) as log_file:
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
