private  void populateTableExecutionContextList(org.apache.hudi.common.config.TypedProperties properties, java.lang.String  configFolder,  org.apache.hadoop.fs.FileSystem fs,
org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Config config) throws java.io.IOException { java.util.List<java.lang.String> tablesToBeIngested
        =  getTablesToBeIngested(properties);

        org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.logger.info("tables to be ingested via MultiTableDeltaStreamer : "
        + tablesToBeIngested); org.apache.hudi.utilities.streamer.TableExecutionContext executionContext;
        for (java.lang.String table  :
        tablesToBeIngested)
        {
            java.lang.String[] tableWithDatabase =  table.split("\\.");java.lang.String database =  (tableWithDatabase.length > 1) ? tableWithDatabase[0] : "default"; java.lang.String currentTable
            =
            (tableWithDatabase.length > 1)
            ? tableWithDatabase[1] : table;java.lang.String  configProp = (((org.apache.hudi.utilities.config.HoodieStreamerConfig.INGESTION_PREFIX  + database)
            +  org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Constants.DELIMITER)  + currentTable) + org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Constants.INGESTION_CONFIG_SUFFIX;
            java.lang.String  oldConfigProp
            = (((org.apache.hudi.utilities.config.HoodieStreamerConfig.OLD_INGESTION_PREFIX + database) +
            org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Constants.DELIMITER)
            +  currentTable) + org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Constants.INGESTION_CONFIG_SUFFIX;
            java.lang.String configFilePath = getStringWithAltKeys(properties,  configProp, oldConfigProp, org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Helpers.m0(configFolder,  database,
            currentTable));

            checkIfTableConfigFileExists(configFolder,
            fs, configFilePath); org.apache.hudi.common.config.TypedProperties tableProperties =
            org.apache.hudi.utilities.UtilHelpers.readConfig(fs.getConf(), new org.apache.hadoop.fs.Path(configFilePath), new  java.util.ArrayList<>()).getProps();
            properties.forEach(( k, v) -> {

            if
            (tableProperties.get(k) ==  null) { tableProperties.setProperty(k.toString(), v.toString());
                    }
                }); final org.apache.hudi.utilities.streamer.HoodieStreamer.Config  cfg =
                new org.apache.hudi.utilities.streamer.HoodieStreamer.Config(); 

                java.lang.String targetBasePath = org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.resetTarget(config, database, currentTable); org.apache.hudi.utilities.streamer.HoodieMultiTableStreamer.Helpers.deepCopyConfigs(config, cfg);
                java.lang.String overriddenTargetBasePath = getStringWithAltKeys(tableProperties,
                org.apache.hudi.utilities.config.HoodieStreamerConfig.TARGET_BASE_PATH, true); cfg.targetBasePath  =
                (org.apache.hudi.common.util.StringUtils.isNullOrEmpty(overriddenTargetBasePath)) ?  targetBasePath : overriddenTargetBasePath;
                if (cfg.enableMetaSync && org.apache.hudi.common.util.StringUtils.isNullOrEmpty(tableProperties.getString(org.apache.hudi.sync.common.HoodieSyncConfig.META_SYNC_TABLE_NAME.key(), ""))) {
                    throw
                    new org.apache.hudi.exception.HoodieException("Meta sync table field not provided!");

                }