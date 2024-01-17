/**
 * Examines the children of the branch node and returns true if a node is in
 * that branch
 *
 * @param node
 * 		The node to search for
 * @param branch
 * 		The branch to search in
 * @return True if found, false if not found
 */
private boolean  nodeIsInBranch(com.vaadin.v7.client.ui.VTree.TreeNode node,   com.vaadin.v7.client.ui.VTree.TreeNode branch) { if  (node  ==   branch)   {
        return  true;
    }
    for  (com.vaadin.v7.client.ui.VTree.TreeNode   child   :   branch.getChildren()) {
        if    (child   == node)     {
            return  true; }
        if   ((!child.isLeaf())    &&   child.getState())  {
            if    (nodeIsInBranch(node,  child))    {
                return true;
            }
        }
    }
    return  false; }