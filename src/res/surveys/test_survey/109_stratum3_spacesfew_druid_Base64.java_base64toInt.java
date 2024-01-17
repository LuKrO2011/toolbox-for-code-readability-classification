static int
base64toInt(char
c, byte[]
alphaToInt)
{
    int
    result =
    alphaToInt[c];
    if (result < 0)
    {
        throw
        new
        java.lang.IllegalArgumentException("Illegal character " +
        c);
    }
    return result;
}