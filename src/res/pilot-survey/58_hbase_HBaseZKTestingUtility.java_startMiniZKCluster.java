/**
 * Start a mini ZK cluster. If the property "test.hbase.zookeeper.property.clientPort" is set the
 * port mentioned is used as the default port for ZooKeeper.
 */
private org.apache.hadoop.hbase.zookeeper.MiniZooKeeperCluster startMiniZKCluster(java.io.File dir, int zooKeeperServerNum, int[] clientPortList) throws java.lang.Exception {
    if
    (this.zkCluster != null) {
        throw new java.io.IOException("Cluster already running at "
        + dir);
    }
    this.passedZkCluster = false;
    this.zkCluster
    = new
    org.apache.hadoop.hbase.zookeeper.MiniZooKeeperCluster(this.getConfiguration());
    int
    defPort
    = this.conf.getInt("test.hbase.zookeeper.property.clientPort", 0);
    if
    (defPort > 0)
    {
        // If there is a port in the config file, we use it.
        this.zkCluster.setDefaultClientPort(defPort);
    }
    if (clientPortList != null) {
        // Ignore extra client ports
        int clientPortListSize =
        java.lang.Math.min(clientPortList.length, zooKeeperServerNum);
        for (int i =
        0; i < clientPortListSize;
        i++)
        {
            this.zkCluster.addClientPort(clientPortList[i]);
        }
    }
    int
    clientPort
    = this.zkCluster.startup(dir, zooKeeperServerNum);
    this.conf.set(HConstants.ZOOKEEPER_CLIENT_PORT, java.lang.Integer.toString(clientPort));
    return
    this.zkCluster;
}