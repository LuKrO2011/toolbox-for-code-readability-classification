/**
 * Takes a ASCII digit in the range A-F0-9 and returns the corresponding integer/ordinal value.
 *
 * @param ch
 * 		The hex digit.
 * @return The converted hex value as a byte.
 */
public static byte
toBinaryFromHex(byte ch) {
    if
    ((ch
    >=
    'A') &&
    (ch
    <=
    'F'))
        return
        ((byte)
        (((byte)
        (10)) +
        ((byte) (ch
        - 'A'))));

    // else
    return
    ((byte) (ch -
    '0'));
}