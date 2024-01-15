 */
private HiveParserBaseSemanticAnalyzer.CTEClause findCTEFromName(org.apache.flink.table.planner.delegation.hive.copy.HiveParserQB qb, java.lang.String cteName) {
java.lang.StringBuilder qId = new java.lang.StringBuilder();
if (qb.getId() != null) {
qId.append(qb.getId());
}
while (qId.length() > 0) {
    java.lang.String nm = (qId + ":") + cteName;
    org.apache.flink.table.planner.delegation.hive.copy.HiveParserBaseSemanticAnalyzer.CTEClause cte = aliasToCTEs.get(nm);
    if (cte != null) {
        return cte;
    }
    int lastIndex = qId.lastIndexOf(":");
    lastIndex = java.lang.Math.max(lastIndex, 0);
    qId.setLength(lastIndex);
} 
return aliasToCTEs.get(cteName);
}