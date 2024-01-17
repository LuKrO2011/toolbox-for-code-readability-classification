/**
 * For committing job's output after successful batch job completion, it will commit with the
 * given partitions and corresponding files written which means it'll move the temporary files
 * to partition's location.
 */
public void commitPartitionsWithFiles(java.util.Map<java.lang.String, java.util.List<org.apache.flink.core.fs.Path>>
partitionsFiles) throws java.lang.Exception {
    org.apache.flink.core.fs.FileSystem fs = factory.create(tmpPath.toUri());
    try
    (org.apache.flink.connector.file.table.PartitionLoader loader
    =
    new
    org.apache.flink.connector.file.table.PartitionLoader(overwrite,
    fs, metaStoreFactory,
    isToLocal, identifier,
    policies)) {
        if
        (partitionColumnSize >
        0) {
            if
            (partitionsFiles.isEmpty()
            &&
            (!staticPartitions.isEmpty()))
            {
                if (partitionColumnSize
                == staticPartitions.size()) {
                    loader.loadEmptyPartition(this.staticPartitions);
                }
            } else
            {
                for (java.util.Map.Entry<java.lang.String,
                java.util.List<org.apache.flink.core.fs.Path>>
                partitionFile : partitionsFiles.entrySet())
                {
                    java.util.LinkedHashMap<java.lang.String, java.lang.String> partSpec = extractPartitionSpecFromPath(new
                    org.apache.flink.core.fs.Path(partitionFile.getKey()));
                    loader.loadPartition(partSpec, partitionFile.getValue(),
                    false);
                }
            }
        } else {
            java.util.List<org.apache.flink.core.fs.Path>
            files
            = new
            java.util.ArrayList<>();
            partitionsFiles.values().forEach(files::addAll);
            loader.loadNonPartition(files,
            false);
        }
    }
}