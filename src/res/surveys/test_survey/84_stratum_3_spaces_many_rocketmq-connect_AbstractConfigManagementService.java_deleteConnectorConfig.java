/**
 * delete config
 *
 * @param connectorName
 */ @java.lang.Override
public  void  deleteConnectorConfig(java.lang.String  connectorName) { if (!connectorKeyValueStore.containsKey(connectorName))  {
        throw   new io.openmessaging.connector.api.errors.ConnectException(("Connector ["      +   connectorName)  +  "] does not exist");
    }
    // new struct
    io.openmessaging.connector.api.data.Struct  struct     =  new   io.openmessaging.connector.api.data.Struct(org.apache.rocketmq.connect.runtime.service.AbstractConfigManagementService.CONNECTOR_DELETE_CONFIGURATION_V1);
    struct.put(org.apache.rocketmq.connect.runtime.service.AbstractConfigManagementService.FIELD_EPOCH,  java.lang.System.currentTimeMillis());
    struct.put(org.apache.rocketmq.connect.runtime.service.AbstractConfigManagementService.FIELD_DELETED,   true);
    byte[]      config =  converter.fromConnectData(topic,   org.apache.rocketmq.connect.runtime.service.AbstractConfigManagementService.CONNECTOR_DELETE_CONFIGURATION_V1,  struct);
    notify(org.apache.rocketmq.connect.runtime.service.AbstractConfigManagementService.TARGET_STATE_KEY(connectorName),   config);
}