//commonProps are passed as parameter which contain table to config file mapping
private void populateTableExecutionContextList(TypedProperties properties, String configFolder, FileSystem fs, Config config) throws IOException {
  List<String> tablesToBeIngested = getTablesToBeIngested(properties);
  logger.info("tables to be ingested via MultiTableDeltaStreamer : " + tablesToBeIngested);
  TableExecutionContext executionContext;
  for (String table : tablesToBeIngested) {
    String[] tableWithDatabase = table.split("\\.");
    String database = tableWithDatabase.length > 1 ? tableWithDatabase[0] : "default";
    String currentTable = tableWithDatabase.length > 1 ? tableWithDatabase[1] : table;
    String configProp = HoodieStreamerConfig.INGESTION_PREFIX + database + Constants.DELIMITER + currentTable + Constants.INGESTION_CONFIG_SUFFIX;
    String oldConfigProp = HoodieStreamerConfig.OLD_INGESTION_PREFIX + database + Constants.DELIMITER + currentTable + Constants.INGESTION_CONFIG_SUFFIX;
    String configFilePath = getStringWithAltKeys(properties, configProp, oldConfigProp,
        Helpers.getDefaultConfigFilePath(configFolder, database, currentTable));
    checkIfTableConfigFileExists(configFolder, fs, configFilePath);
    TypedProperties tableProperties = UtilHelpers.readConfig(fs.getConf(), new Path(configFilePath), new ArrayList<>()).getProps();
    properties.forEach((k, v) -> {
      if (tableProperties.get(k) == null) {
        tableProperties.setProperty(k.toString(), v.toString());
      }
    });
    final HoodieStreamer.Config cfg = new HoodieStreamer.Config();
    //copy all the values from config to cfg
    String targetBasePath = resetTarget(config, database, currentTable);
    Helpers.deepCopyConfigs(config, cfg);
    String overriddenTargetBasePath = getStringWithAltKeys(tableProperties, HoodieStreamerConfig.TARGET_BASE_PATH, true);
    cfg.targetBasePath = StringUtils.isNullOrEmpty(overriddenTargetBasePath) ? targetBasePath : overriddenTargetBasePath;
    if (cfg.enableMetaSync && StringUtils.isNullOrEmpty(tableProperties.getString(HoodieSyncConfig.META_SYNC_TABLE_NAME.key(), ""))) {
      throw new HoodieException("Meta sync table field not provided!");
    }
    populateTransformerProps(cfg, tableProperties);
    populateSchemaProviderProps(cfg, tableProperties);
    executionContext = new TableExecutionContext();
    executionContext.setProperties(tableProperties);
    executionContext.setConfig(cfg);
    executionContext.setDatabase(database);
    executionContext.setTableName(currentTable);
    this.tableExecutionContexts.add(executionContext);
  }
}