private org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFInputSpec processPTFSource(org.apache.flink.table.planner.delegation.hive.copy.HiveParserQB qb, org.apache.flink.table.planner.delegation.hive.copy.HiveParserASTNode inputNode) throws org.apache.hadoop.hive.ql.parse.SemanticException {
    org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFInputSpec qInSpec = null;
    int type = inputNode.getType();
    java.lang.String alias;
    switch (type) {
        case org.apache.flink.table.planner.delegation.hive.parse.HiveASTParser.TOK_TABREF :
            alias = processTable(qb, inputNode);
            qInSpec = new org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFQueryInputSpec();
            ((org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFQueryInputSpec) (qInSpec)).setType(org.apache.hadoop.hive.ql.parse.PTFInvocationSpec.PTFQueryInputType.TABLE);
            ((org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFQueryInputSpec) (qInSpec)).setSource(alias);
            break;
        case org.apache.flink.table.planner.delegation.hive.parse.HiveASTParser.TOK_SUBQUERY :
            alias = processSubQuery(qb, inputNode);
            qInSpec = new org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFQueryInputSpec();
            ((org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFQueryInputSpec) (qInSpec)).setType(org.apache.hadoop.hive.ql.parse.PTFInvocationSpec.PTFQueryInputType.SUBQUERY);
            ((org.apache.flink.table.planner.delegation.hive.copy.HiveParserPTFInvocationSpec.PTFQueryInputSpec) (qInSpec)).setSource(alias);
            break;
        case org.apache.flink.table.planner.delegation.hive.parse.HiveASTParser.TOK_PTBLFUNCTION :
            qInSpec = processPTFChain(qb, inputNode);
            break;
        default :
            throw new org.apache.hadoop.hive.ql.parse.SemanticException(org.apache.flink.table.planner.delegation.hive.HiveParserUtils.generateErrorMessage(inputNode, "Unknown input type to PTF"));
    }
    qInSpec.setAstNode(inputNode);
    return qInSpec;
}