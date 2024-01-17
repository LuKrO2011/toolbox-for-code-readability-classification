* Sets the width of the cell. This width should not include any
* possible indent modifications that are present in
* {@link VScrollTableBody#getMaxIndent()}.
*
* @param w
* 		The width of the cell
* @param ensureDefinedWidth
* 		Ensures that the given width is not recalculated
*/public void setWidth(int w, boolean ensureDefinedWidth) { if (ensureDefinedWidth) {definedWidth = true;// on column resize expand ratio becomes zero
       expandRatio = 0;
   }if (width == w) { return;}if (width == (-1)) {// go to default mode, clip content if necessary
       captionContainer.getStyle().clearOverflow();}width = w;
   if (w == (-1)) {
       captionContainer.getStyle().clearWidth();
       setWidth(""); } else {/* Reduce width with one pixel for the right border since the
       footers does not have any spacers between them.
        */
       final int borderWidths = 1;// Set the container width (check for negative value)
       captionContainer.getStyle().setPropertyPx("width", java.lang.Math.max(w - borderWidths, 0));/* if we already have tBody, set the header width properly, if
       not defer it. IE will fail with complex float in table header
       unless TD width is not explicitly set.
        */if (scrollBody != null) {
           int maxIndent = scrollBody.getMaxIndent();
           if ((w < maxIndent) && (tFoot.visibleCells.indexOf(this) == getHierarchyColumnIndex())) {
               // ensure there's room for the indent
               w = maxIndent;
           } int tdWidth = (w + scrollBody.getCellExtraWidth()) - borderWidths;
           setWidth(java.lang.Math.max(tdWidth, 0) + "px");} else {com.google.gwt.core.client.Scheduler.get().scheduleDeferred(new com.google.gwt.user.client.Command() { @java.lang.Override public void execute() {int tdWidth = width;int maxIndent = scrollBody.getMaxIndent();if ((tdWidth < maxIndent) && (tFoot.visibleCells.indexOf(this) == getHierarchyColumnIndex())) {
                       // ensure there's room for the indent
                       tdWidth = maxIndent;}tdWidth += scrollBody.getCellExtraWidth() - borderWidths;setWidth(java.lang.Math.max(tdWidth, 0) + "px");}});}}}