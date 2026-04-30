base64_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
base64_indexes = {char: i for i, char in enumerate(base64_chars)}


def encode_base64(n: int) -> str:
    '''
    Convert an integer to a base 64 string.

    >>> encode_base64(0)
    'A'
    >>> encode_base64(1)
    'B'
    >>> encode_base64(63)
    '_'
    >>> encode_base64(64)
    'BA'
    >>> encode_base64(100_000)
    'Yag'
    '''
    result = ''

    while n > 0:
        trailing_bits = n % 64
        result = base64_chars[trailing_bits] + result
        n = n // 64

    if result == '':
        return 'A'
    return result


def decode_base64(s: str) -> int:
    '''
    Convert a base 64 string to an integer.

    >>> decode_base64('A')
    0
    >>> decode_base64('B')
    1
    >>> decode_base64('_')
    63
    >>> decode_base64('BA')
    64
    >>> decode_base64('Yag')
    100000
    '''
    result = 0
    for i, char in enumerate(reversed(s)):
        result += base64_indexes[char] * 64**i
    return result
