@Override
public void updateLatestBlockSizes(HFileContext context, int uncompressed, int compressed) {
    configuredMaxBlockSize = context.getBlocksize();
    compressionRatio = uncompressed / compressed;
    adjustedBlockSize = context.getBlocksize() * compressionRatio;
}