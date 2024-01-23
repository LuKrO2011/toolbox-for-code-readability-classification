/**
 * Recalculates compression rate for the last block and adjusts the block size limit as:
 * BLOCK_SIZE * (uncompressed/compressed).
 * @param context      HFIleContext containing the configured max block size.
 * @param uncompressed the uncompressed size of last block written.
 * @param compressed   the compressed size of last block written.
 */
@Override
public void updateLatestBlockSizes(HFileContext context, int uncompressed, int compressed) {
  configuredMaxBlockSize = context.getBlocksize();
  compressionRatio = uncompressed / compressed;
  adjustedBlockSize = context.getBlocksize() * compressionRatio;
}