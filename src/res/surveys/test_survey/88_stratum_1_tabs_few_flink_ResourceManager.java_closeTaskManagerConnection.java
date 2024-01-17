/**
 * This method should be called by the framework once it detects that a currently registered
 * task executor has failed.
 *
 * @param resourceID
 * 		Id of the TaskManager that has failed.
 * @param cause
 * 		The exception which cause the TaskManager failed.
 * @return The {@link WorkerType} of the closed connection, or empty if already removed.
 */
protected java.util.Optional<WorkerType> closeTaskManagerConnection(final org.apache.flink.runtime.clusterframework.types.ResourceID resourceID, final java.lang.Exception cause) {
    taskManagerHeartbeatManager.unmonitorTarget(resourceID);
    org.apache.flink.runtime.resourcemanager.registration.WorkerRegistration<WorkerType> workerRegistration = taskExecutors.remove(resourceID);
    if (workerRegistration != null) {
    log.info("Closing TaskExecutor connection {} because: {}", resourceID.getStringWithMetadata(), cause.getMessage(), org.apache.flink.util.ExceptionUtils.returnExceptionIfUnexpected(cause.getCause()));
    org.apache.flink.util.ExceptionUtils.logExceptionIfExcepted(cause.getCause(), log);
    // TODO :: suggest failed task executor to stop itself
    slotManager.unregisterTaskManager(workerRegistration.getInstanceID(), cause);
    clusterPartitionTracker.processTaskExecutorShutdown(resourceID);
    workerRegistration.getTaskExecutorGateway().disconnectResourceManager(cause);
    } else {
        log.debug("No open TaskExecutor connection {}. Ignoring close TaskExecutor connection. Closing reason was: {}", resourceID.getStringWithMetadata(), cause.getMessage());
        }
        return java.util.Optional.ofNullable(workerRegistration).map(WorkerRegistration::getWorker);
        }