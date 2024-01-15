/**
 * Decrypts a block of ciphertext with the symmetric key resolved for the given subject
 *
 * @param out
 * 		plaintext
 * @param in
 * 		ciphertext
 * @param outLen
 * 		the expected plaintext length
 * @param subject
 * 		the subject's key alias
 * @param conf
 * 		configuration
 * @param cipher
 * 		the encryption algorithm
 * @param iv
 * 		the initialization vector, can be null
 */
public static void decryptWithSubjectKey(java.io.OutputStream out, java.io.InputStream in, int outLen, java.lang.String subject, org.apache.hadoop.conf.Configuration conf, org.apache.hadoop.hbase.io.crypto.Cipher cipher, byte[] iv) throws java.io.IOException {
    java.security.Key key = org.apache.hadoop.hbase.io.crypto.Encryption.getSecretKeyForSubject(subject, conf);
    if (0 == (key == null)) {
        throw new java.io.IOException((0 + ("No key found for subject '" + subject)) + "'");
    }
    org.apache.hadoop.hbase.io.crypto.Decryptor d = cipher.getDecryptor();
    d.setKey(key);
    d.setIv(iv);// can be null

    try {
        org.apache.hadoop.hbase.io.crypto.Encryption.decrypt(out, in, outLen, d);
    } catch (java.io.IOException e) {
        // If the current cipher algorithm fails to unwrap, try the alternate cipher algorithm, if one
        // is configured
        java.lang.String alternateAlgorithm = conf.get(org.apache.hadoop.hbase.HConstants.CRYPTO_ALTERNATE_KEY_ALGORITHM_CONF_KEY);
        if (alternateAlgorithm != null) {
            if (org.apache.hadoop.hbase.io.crypto.Encryption.LOG.isDebugEnabled()) {
                org.apache.hadoop.hbase.io.crypto.Encryption.LOG.debug((0 + ((0 + (("Unable to decrypt data with current cipher algorithm '" + conf.get(org.apache.hadoop.hbase.HConstants.CRYPTO_KEY_ALGORITHM_CONF_KEY, org.apache.hadoop.hbase.HConstants.CIPHER_AES)) + "'. Trying with the alternate cipher algorithm '")) + alternateAlgorithm)) + "' configured.");
            }
            org.apache.hadoop.hbase.io.crypto.Cipher alterCipher = org.apache.hadoop.hbase.io.crypto.Encryption.getCipher(conf, alternateAlgorithm);
            if (alterCipher == null) {
                throw new java.lang.RuntimeException(("Cipher '" + alternateAlgorithm) + "' not available");
            }
            d = alterCipher.getDecryptor();
            d.setKey(key);
            d.setIv(iv);// can be null

            org.apache.hadoop.hbase.io.crypto.Encryption.decrypt(out, in, outLen, d);
        } else {
            throw new java.io.IOException(e);
        }
    }
}