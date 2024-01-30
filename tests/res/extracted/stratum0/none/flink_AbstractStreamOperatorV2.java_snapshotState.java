/**
 * Stream operators with state, which want to participate in a snapshot need to override this
 * hook method.
 *
 * @param context
 * 		context that provides information and means required for taking a snapshot
 */
@Override
public void snapshotState(StateSnapshotContext context) throws Exception {
}