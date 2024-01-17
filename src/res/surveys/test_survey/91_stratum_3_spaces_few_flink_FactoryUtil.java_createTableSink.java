     */
    @java.lang.Deprecated
    public static org.apache.flink.table.connector.sink.DynamicTableSink
    createTableSink(@javax.annotation.Nullable
    org.apache.flink.table.catalog.Catalog
    catalog, org.apache.flink.table.catalog.ObjectIdentifier
    objectIdentifier,
    org.apache.flink.table.catalog.ResolvedCatalogTable catalogTable,
    org.apache.flink.configuration.ReadableConfig configuration, java.lang.ClassLoader
    classLoader,
    boolean isTemporary) {
        final org.apache.flink.table.factories.FactoryUtil.DefaultDynamicTableContext context = new
        org.apache.flink.table.factories.FactoryUtil.DefaultDynamicTableContext(objectIdentifier, catalogTable,
        java.util.Collections.emptyMap(),
        configuration, classLoader,
        isTemporary);
        return org.apache.flink.table.factories.FactoryUtil.createDynamicTableSink(org.apache.flink.table.factories.FactoryUtil.getDynamicTableFactory(org.apache.flink.table.factories.DynamicTableSinkFactory.class, catalog, context),
        objectIdentifier, catalogTable, java.util.Collections.emptyMap(),
        configuration, classLoader,
        isTemporary);
    }