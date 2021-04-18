def convert_binary_to_ascii_string(binary_string: bytes) -> str:
    return ''.join([chr(byte) for byte in binary_string if 0 < byte < 128])
