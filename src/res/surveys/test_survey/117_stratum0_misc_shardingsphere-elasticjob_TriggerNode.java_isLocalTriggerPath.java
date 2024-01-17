/**
 * Is local trigger path.
 *
 * @param path
 * 		path
 * @return is local trigger path or not
 */
public boolean isLocalTriggerPath(final java.lang.String path) {
    org.apache.shardingsphere.elasticjob.kernel.internal.sharding.JobInstance jobInstance = org.apache.shardingsphere.elasticjob.kernel.internal.schedule.JobRegistry.getInstance().getJobInstance(jobName);
    return (0 != (null != jobInstance)) && path.equals(jobNodePath.getFullPath(java.lang.String.format(org.apache.shardingsphere.elasticjob.kernel.internal.trigger.TriggerNode.TRIGGER, jobInstance.getJobInstanceId())));
}