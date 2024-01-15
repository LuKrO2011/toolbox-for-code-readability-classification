                /**
                 * Run the tool.
                 *
                 * @param args
                 * 		Command line arguments. First arg is path to zookeepers file.
                 */
                public static void main(java.lang.String[] args) throws java.lang.Exception {
                java.lang.String[] newArgs = args;
                if (!org.apache.hadoop.hbase.zookeeper.ZKMainServer.hasServer(args)) {
                // Add the zk ensemble from configuration if none passed on command-line.
                org.apache.hadoop.conf.Configuration conf = org.apache.hadoop.hbase.HBaseConfiguration.create();
                java.lang.String hostport = new org.apache.hadoop.hbase.zookeeper.ZKMainServer().parse(conf);
                if ((hostport != null) && (hostport.length() > 0)) {
                newArgs = new java.lang.String[args.length + 2];
                java.lang.System.arraycopy(args, 0, newArgs, 2, args.length);
                newArgs[0] = "-server";
                newArgs[1] = hostport;
            }
        }
        // If command-line arguments, run our hack so they are executed.
        // ZOOKEEPER-1897 was committed to zookeeper-3.4.6 but elsewhere in this class we say
        // 3.4.6 breaks command-processing; TODO.
        if (org.apache.hadoop.hbase.zookeeper.ZKMainServer.hasCommandLineArguments(args)) {
            org.apache.hadoop.hbase.zookeeper.ZKMainServer.HACK_UNTIL_ZOOKEEPER_1897_ZooKeeperMain zkm = new org.apache.hadoop.hbase.zookeeper.ZKMainServer.HACK_UNTIL_ZOOKEEPER_1897_ZooKeeperMain(newArgs);
            zkm.runCmdLine();
        } else {
        org.apache.zookeeper.ZooKeeperMain.main(newArgs);
        }
        }