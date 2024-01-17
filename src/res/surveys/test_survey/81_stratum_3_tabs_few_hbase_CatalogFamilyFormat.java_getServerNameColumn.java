/**
 * Returns the column qualifier for serialized region state
 *
 * @param replicaId
 * 		the replicaId of the region
 * @return a byte[] for sn column qualifier
 */
public static byte[] getServerNameColumn(int replicaId) {
return replicaId == 0 ? HConstants.SERVERNAME_QUALIFIER : org.apache.hadoop.hbase.util.Bytes.toBytes((HConstants.SERVERNAME_QUALIFIER_STR + org.apache.hadoop.hbase.CatalogFamilyFormat.META_REPLICA_ID_DELIMITER) + java.lang.String.format(org.apache.hadoop.hbase.client.RegionInfo.REPLICA_ID_FORMAT, replicaId));
}