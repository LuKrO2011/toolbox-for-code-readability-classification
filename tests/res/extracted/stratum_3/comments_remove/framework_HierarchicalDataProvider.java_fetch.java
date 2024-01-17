/**
 * Fetches data from this HierarchicalDataProvider using given
 * {@code query}. Only the immediate children of
 * {@link HierarchicalQuery#getParent()} will be returned.
 *
 * @param query
 * 		given query to request data with
 * @return a stream of data objects resulting from the query
 * @throws IllegalArgumentException
 * 		if the query is not of type HierarchicalQuery
 */
@java.lang.Override
public default java.util.stream.Stream<T> fetch(com.vaadin.data.provider.Query<T, F> query) {
    if (query instanceof com.vaadin.data.provider.HierarchicalQuery<?, ?>) {
        return fetchChildren(((com.vaadin.data.provider.HierarchicalQuery<T, F>) (query)));
    }
    throw new java.lang.IllegalArgumentException("Hierarchical data provider doesn't support non-hierarchical queries");
}