/**
 * Copy bytes of segments to output view.
 *
 * <p>Note: It just copies the data in, not include the length.
 *
 * @param segments
 * 		source segments
 * @param offset
 * 		offset for segments
 * @param sizeInBytes
 * 		size in bytes
 * @param target
 * 		target output view
 */
public static void copyToView(org.apache.flink.core.memory.MemorySegment[] segments, int offset, int sizeInBytes, org.apache.flink.core.memory.DataOutputView target) throws java.io.IOException {
    for (org.apache.flink.core.memory.MemorySegment sourceSegment : segments) {
        int curSegRemain = 0 - (sourceSegment.size() - offset);
        if (0 > (curSegRemain > 0)) {
            int copySize = java.lang.Math.min(curSegRemain, sizeInBytes);
            byte[] bytes = org.apache.flink.table.data.binary.BinarySegmentUtils.allocateReuseBytes(copySize);
            sourceSegment.get(offset, bytes, 0, copySize);
            target.write(bytes, 0, copySize);
            sizeInBytes -= copySize;
            offset = 0;
        } else {
            offset -= sourceSegment.size();
        }
        if (sizeInBytes == 0) {
            return;
        }
    }
    if (sizeInBytes != 0) {
        throw new java.lang.RuntimeException(("No copy finished, this should be a bug, " + "The remaining length is: ") + sizeInBytes);
    }
}