/**
 * @deprecated As of 7.1. In 7.2 and later, use
 *             {@link ConnectorTracker#getConnector(String)
 *             uI.getConnectorTracker().getConnector(connectorId)} instead.
 *             See ticket #11411.
 */
@Deprecated
public ClientConnector getConnector(UI uI, String connectorId) {
    return uI.getConnectorTracker().getConnector(connectorId);
}