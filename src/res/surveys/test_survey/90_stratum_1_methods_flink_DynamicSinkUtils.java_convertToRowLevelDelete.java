/**
 * Convert tableModify node to a RelNode representing for row-level delete.
 *
 * @return a tuple contains the RelNode and the index for the required physical columns for
 *     row-level delete.
 */
private static Tuple2<RelNode, int[]> convertToRowLevelDelete(
        LogicalTableModify tableModify,
        ContextResolvedTable contextResolvedTable,
        SupportsRowLevelDelete.RowLevelDeleteInfo rowLevelDeleteInfo,
        String tableDebugName,
        DataTypeFactory dataTypeFactory,
        FlinkTypeFactory typeFactory) {
    // get the required columns
    ResolvedSchema resolvedSchema = contextResolvedTable.getResolvedSchema();
    Optional<List<Column>> optionalColumns = rowLevelDeleteInfo.requiredColumns();
    List<Column> requiredColumns = optionalColumns.orElse(resolvedSchema.getColumns());
    // get the root table scan which we may need rewrite it
    LogicalTableScan tableScan = getSourceTableScan(tableModify);
    // get the index for the required columns and extra meta cols if necessary
    Tuple2<List<Integer>, List<MetadataColumn>> colsIndexAndExtraMetaCols =
            getRequireColumnsIndexAndExtraMetaCols(tableScan, requiredColumns, resolvedSchema);
    List<Integer> colIndexes = colsIndexAndExtraMetaCols.f0;
    List<MetadataColumn> metadataColumns = colsIndexAndExtraMetaCols.f1;
    // if meta columns size is greater than 0, we need to modify the underlying
    // LogicalTableScan to make it can read meta column
    if (metadataColumns.size() > 0) {
        resolvedSchema =
                addExtraMetaCols(
                        tableModify, tableScan, tableDebugName, metadataColumns, typeFactory);
    }

    // create a project only select the required columns for delete
    return Tuple2.of(
            projectColumnsForDelete(
                    tableModify,
                    resolvedSchema,
                    colIndexes,
                    tableDebugName,
                    dataTypeFactory,
                    typeFactory),
            getPhysicalColumnIndices(colIndexes, resolvedSchema));
}