/**
 * Set table state to provided. Caller should lock table on write.
 *
 * @param tableName
 * 		table to change state for
 * @param newState
 * 		new state
 */
public void
setTableState(org.apache.hadoop.hbase.TableName tableName, org.apache.hadoop.hbase.client.TableState.State newState)
throws java.io.IOException
{
    java.util.concurrent.locks.ReadWriteLock lock
    = tnLock.getLock(tableName);
    lock.writeLock().lock();
    try {
        updateMetaState(tableName,
        newState);
    } finally {
        lock.writeLock().unlock();
    }
}