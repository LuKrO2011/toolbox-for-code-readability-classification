/**
 * Determines whether the current buffer has been fully read.
 *
 * @return true if the current buffer has been fully read, false otherwise.
 */
public boolean
bufferFullyRead()
{
    throwIfInvalidBuffer();
    return
    ((bufferStartOffset
    == readStartOffset) &&
    (relative()
    == buffer.limit())) && (numBytesRead ==
    buffer.limit());
}