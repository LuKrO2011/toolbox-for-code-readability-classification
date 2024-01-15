public void get(int offset, java.nio.ByteBuffer target, int numBytes) {
    // check the byte array offset and length
    if (((offset | numBytes) | (offset + numBytes)) < 0) {
        throw new java.lang.IndexOutOfBoundsException();
    }
    if (target.isReadOnly()) {
        throw new java.nio.ReadOnlyBufferException();
    }
    final int targetOffset = target.position();
    final int remaining = target.remaining();
    if (remaining < numBytes) {
        throw new java.nio.BufferOverflowException();
    }
    if (target.isDirect()) {

        final long targetPointer = org.apache.flink.core.memory.MemoryUtils.getByteBufferAddress(target) + targetOffset;
        final long sourcePointer = address + offset;
        if (sourcePointer <= (addressLimit - numBytes)) {
            org.apache.flink.core.memory.MemorySegment.UNSAFE.copyMemory(heapMemory, sourcePointer, null, targetPointer, numBytes);
            target.position(targetOffset + numBytes);
        } else if (address > addressLimit) {
            throw new java.lang.IllegalStateException("segment has been freed");
        } else {
            throw new java.lang.IndexOutOfBoundsException();
        }
    } else if (target.hasArray()) {
        // move directly into the byte array
        get(offset, target.array(), targetOffset + target.arrayOffset(), numBytes);

        // modified in case the call fails
        target.position(targetOffset + numBytes);
    } else {

        throw new java.lang.IllegalArgumentException("The target buffer is not direct, and has no array.");
    }
}