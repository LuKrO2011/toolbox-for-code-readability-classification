/**
 * Checks if a given element is a spacer element
 */
public boolean isSpacer(com.google.gwt.dom.client.Element row) {
/* If this needs optimization, we could do a more heuristic check
based on stylenames and stuff, instead of iterating through the
map.
 */
for (com.vaadin.v7.client.widgets.Escalator.SpacerContainer.SpacerImpl spacer : rowIndexToSpacer.values()) {
if (spacer.getRootElement().equals(row)) {
return true;
}
}
return false;
}