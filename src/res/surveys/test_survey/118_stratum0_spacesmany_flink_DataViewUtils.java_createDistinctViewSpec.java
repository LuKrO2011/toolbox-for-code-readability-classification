/**
 * Creates a special {@link DistinctViewSpec} for DISTINCT aggregates.
 */
public static org.apache.flink.table.planner.typeutils.DataViewUtils.DistinctViewSpec    createDistinctViewSpec(int index, org.apache.flink.table.types.DataType distinctViewDataType) { return  new  org.apache.flink.table.planner.typeutils.DataViewUtils.DistinctViewSpec("distinctAcc_"  +   index,   distinctViewDataType);
}