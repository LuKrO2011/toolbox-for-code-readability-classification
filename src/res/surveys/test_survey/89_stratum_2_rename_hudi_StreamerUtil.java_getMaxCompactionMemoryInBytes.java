/**
 * Returns the max compaction memory in bytes with given conf.
 */
public static long getMaxCompactionMemoryInBytes(org.apache.flink.configuration.Configuration conf) {
    return (((long) (conf.getInteger(org.apache.hudi.configuration.FlinkOptions.COMPACTION_MAX_MEMORY))) * 1024) * 1024;
}