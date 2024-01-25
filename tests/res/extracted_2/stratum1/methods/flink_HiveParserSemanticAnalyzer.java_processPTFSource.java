/*
 * - a partitionTableFunctionSource can be a tableReference, a SubQuery or another
 *   PTF invocation.
 * - For a TABLEREF: set the source to the alias returned by processTable
 * - For a SubQuery: set the source to the alias returned by processSubQuery
 * - For a PTF invocation: recursively call processPTFChain.
 */
private PTFInputSpec processPTFSource(HiveParserQB qb, HiveParserASTNode inputNode)
        throws SemanticException {

    PTFInputSpec qInSpec = null;
    int type = inputNode.getType();
    String alias;
    switch (type) {
        case HiveASTParser.TOK_TABREF:
            alias = processTable(qb, inputNode);
            qInSpec = new PTFQueryInputSpec();
            ((PTFQueryInputSpec) qInSpec).setType(PTFQueryInputType.TABLE);
            ((PTFQueryInputSpec) qInSpec).setSource(alias);
            break;
        case HiveASTParser.TOK_SUBQUERY:
            alias = processSubQuery(qb, inputNode);
            qInSpec = new PTFQueryInputSpec();
            ((PTFQueryInputSpec) qInSpec).setType(PTFQueryInputType.SUBQUERY);
            ((PTFQueryInputSpec) qInSpec).setSource(alias);
            break;
        case HiveASTParser.TOK_PTBLFUNCTION:
            qInSpec = processPTFChain(qb, inputNode);
            break;
        default:
            throw new SemanticException(
                    HiveParserUtils.generateErrorMessage(
                            inputNode, "Unknown input type to PTF"));
    }

    qInSpec.setAstNode(inputNode);
    return qInSpec;
}