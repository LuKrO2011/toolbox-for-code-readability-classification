public static byte toBinaryFromHex(byte ch) {
    if ((ch >= 'A') && (ch <= 'F'))
        return ((byte) (((byte) (10)) + ((byte) (ch - 'A'))));


    return ((byte) (ch - '0'));
}