/**
 *
 * @param flinkContainerCode
 * 		code phrase which represent flink container type like row/array in
 * 		codegen sections
 * @param index
 * 		the index number in flink container type
 * @param eleType
 * 		the element type
 */
public static java.lang.String flinkContainerElementCode(java.lang.String flinkContainerCode, java.lang.String index, org.apache.flink.table.types.logical.LogicalType eleType) {
    switch (eleType.getTypeRoot()) {
        case INTEGER :
            return ((flinkContainerCode + ".getInt(") + index) + ")";
            case BIGINT :
            return ((flinkContainerCode + ".getLong(") + index) + ")";
        case FLOAT :
        return ((flinkContainerCode + ".getFloat(") + index) + ")";
    case DOUBLE :
        return ((flinkContainerCode + ".getDouble(") + index) + ")";
    case BOOLEAN :
        return ((flinkContainerCode + ".getBoolean(") + index) + ")";
        case VARCHAR :
    case CHAR :
        return ((flinkContainerCode + ".getString(") + index) + ")";
        case VARBINARY :
        case BINARY :
            return ((flinkContainerCode + ".getBinary(") + index) + ")";
            case ROW :
                int size = eleType.getChildren().size();
                return ((((flinkContainerCode + ".getRow(") + index) + ", ") + size) + ")";
                case MAP :
                return ((flinkContainerCode + ".getMap(") + index) + ")";
            case ARRAY :
            return ((flinkContainerCode + ".getArray(") + index) + ")";
            default :
            throw new java.lang.IllegalArgumentException("Unsupported data type in schema: " + eleType);
    }
}