* The streaming write pipeline.
*
* <p>The input dataset shuffles by the primary key first then
* shuffles by the file group ID before passing around to the write function.
* The whole pipeline looks like the following:
*
* <pre>
*      | input1 | ===\     /=== | bucket assigner | ===\     /=== | task1 |
*                   shuffle(by PK)                    shuffle(by bucket ID)
*      | input2 | ===/     \=== | bucket assigner | ===/     \=== | task2 |
*
*      Note: a file group must be handled by one write task to avoid write conflict.
* </pre>
*
* <p>The bucket assigner assigns the inputs to suitable file groups, the write task caches
* and flushes the data set to disk.
*
* @param conf
* 		The configuration
* @param dataStream
* 		The input data stream
* @return the stream write data stream pipeline
*/public static org.apache.flink.streaming.api.datastream.DataStream<java.lang.Object> hoodieStreamWrite(org.apache.flink.configuration.Configuration conf, org.apache.flink.streaming.api.datastream.DataStream<org.apache.hudi.common.model.HoodieRecord> dataStream) {if (org.apache.hudi.configuration.OptionsResolver.isBucketIndexType(conf)) {
       org.apache.hudi.index.HoodieIndex.BucketIndexEngineType bucketIndexEngineType = org.apache.hudi.configuration.OptionsResolver.getBucketEngineType(conf);switch (bucketIndexEngineType) {case SIMPLE :
               int bucketNum = conf.getInteger(org.apache.hudi.configuration.FlinkOptions.BUCKET_INDEX_NUM_BUCKETS);java.lang.String indexKeyFields = org.apache.hudi.configuration.OptionsResolver.getIndexKeyField(conf);org.apache.hudi.sink.partitioner.BucketIndexPartitioner<org.apache.hudi.common.model.HoodieKey> partitioner = new org.apache.hudi.sink.partitioner.BucketIndexPartitioner<>(bucketNum, indexKeyFields);return dataStream.partitionCustom(partitioner, HoodieRecord::getKey).transform(org.apache.hudi.sink.utils.Pipelines.opName("bucket_write", conf), org.apache.flink.api.common.typeinfo.TypeInformation.of(java.lang.Object.class), org.apache.hudi.sink.bucket.BucketStreamWriteOperator.getFactory(conf)).uid(org.apache.hudi.sink.utils.Pipelines.opUID("bucket_write", conf)).setParallelism(conf.getInteger(org.apache.hudi.configuration.FlinkOptions.WRITE_TASKS));case CONSISTENT_HASHING :
               if (org.apache.hudi.configuration.OptionsResolver.isInsertOverwrite(conf)) {// TODO support insert overwrite for consistent bucket index
                   throw new org.apache.hudi.exception.HoodieException("Consistent hashing bucket index does not work with insert overwrite using FLINK engine. Use simple bucket index or Spark engine.");
               }
               return dataStream.transform(org.apache.hudi.sink.utils.Pipelines.opName("consistent_bucket_assigner", conf), org.apache.flink.api.common.typeinfo.TypeInformation.of(org.apache.hudi.common.model.HoodieRecord.class), new org.apache.flink.streaming.api.operators.ProcessOperator<>(new org.apache.hudi.sink.bucket.ConsistentBucketAssignFunction(conf))).uid(org.apache.hudi.sink.utils.Pipelines.opUID("consistent_bucket_assigner", conf)).setParallelism(conf.getInteger(org.apache.hudi.configuration.FlinkOptions.BUCKET_ASSIGN_TASKS)).keyBy(( record) -> record.getCurrentLocation().getFileId()).transform(org.apache.hudi.sink.utils.Pipelines.opName("consistent_bucket_write", conf), org.apache.flink.api.common.typeinfo.TypeInformation.of(java.lang.Object.class), org.apache.hudi.sink.bucket.BucketStreamWriteOperator.getFactory(conf)).uid(org.apache.hudi.sink.utils.Pipelines.opUID("consistent_bucket_write", conf)).setParallelism(conf.getInteger(org.apache.hudi.configuration.FlinkOptions.WRITE_TASKS));default :throw new org.apache.hudi.exception.HoodieNotSupportedException("Unknown bucket index engine type: " + bucketIndexEngineType);
       }} else {
       org.apache.hudi.sink.common.WriteOperatorFactory<org.apache.hudi.common.model.HoodieRecord> operatorFactory = org.apache.hudi.sink.StreamWriteOperator.getFactory(conf);return // shuffle by fileId(bucket id)
       // Key-by record key, to avoid multiple subtasks write to a bucket at the same time
       dataStream.keyBy(HoodieRecord::getRecordKey).transform("bucket_assigner", org.apache.flink.api.common.typeinfo.TypeInformation.of(org.apache.hudi.common.model.HoodieRecord.class), new org.apache.flink.streaming.api.operators.KeyedProcessOperator<>(new org.apache.hudi.sink.partitioner.BucketAssignFunction<>(conf))).uid(org.apache.hudi.sink.utils.Pipelines.opUID("bucket_assigner", conf)).setParallelism(conf.getInteger(org.apache.hudi.configuration.FlinkOptions.BUCKET_ASSIGN_TASKS)).keyBy(( record) -> record.getCurrentLocation().getFileId()).transform(org.apache.hudi.sink.utils.Pipelines.opName("stream_write", conf), org.apache.flink.api.common.typeinfo.TypeInformation.of(java.lang.Object.class), operatorFactory).uid(org.apache.hudi.sink.utils.Pipelines.opUID("stream_write", conf)).setParallelism(conf.getInteger(org.apache.hudi.configuration.FlinkOptions.WRITE_TASKS));
   }}