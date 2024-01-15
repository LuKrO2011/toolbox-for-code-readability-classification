static org.apache.hadoop.io.compress.CompressionInputStream createInputStreamWithCodecPool(org.apache.hadoop.io.compress.CompressionCodec codec,
org.apache.hadoop.conf.Configuration conf, java.io.InputStream in)
throws java.io.IOException {

    org.apache.hadoop.io.compress.Decompressor
    decompressor = org.apache.hadoop.io.compress.CodecPool.getDecompressor(codec);

    org.apache.hadoop.io.compress.CompressionInputStream stream = null;

    try {
        stream = codec.createInputStream(in, decompressor);
    } finally
    {

        if (stream == null) {
            org.apache.hadoop.io.compress.CodecPool.returnDecompressor(decompressor);
        } else {



            stream.setTrackedDecompressor(decompressor);


        }

    }

    return stream;
}