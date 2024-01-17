/**
 * Returns max key for the Bloom filter from the configuration
 */
public static int getMaxKeys(org.apache.hadoop.conf.Configuration conf) {
return conf.getInt(org.apache.hadoop.hbase.util.BloomFilterFactory.IO_STOREFILE_BLOOM_MAX_KEYS, (128 * 1000) * 1000);
}

/**
 * Creates a new general (Row or RowCol) Bloom filter at the time of
 * {@link org.apache.hadoop.hbase.regionserver.HStoreFile}