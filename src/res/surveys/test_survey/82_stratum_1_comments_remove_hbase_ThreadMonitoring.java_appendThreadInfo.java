public static void appendThreadInfo(java.lang.StringBuilder sb, java.lang.management.ThreadInfo info, java.lang.String indent) {
    boolean contention = org.apache.hadoop.hbase.monitoring.ThreadMonitoring.threadBean.isThreadContentionMonitoringEnabled();
    if (info == null) {
        sb.append(indent).append("Inactive (perhaps exited while monitoring was done)\n");
        return;
    }
    java.lang.String taskName = org.apache.hadoop.hbase.monitoring.ThreadMonitoring.getTaskName(info.getThreadId(), info.getThreadName());
    sb.append(indent).append("Thread ").append(taskName).append(":\n");
    java.lang.Thread.State state = info.getThreadState();
    sb.append(indent).append("  State: ").append(state).append("\n");
    sb.append(indent).append("  Blocked count: ").append(info.getBlockedCount()).append("\n");
    sb.append(indent).append("  Waited count: ").append(info.getWaitedCount()).append("\n");
    if (contention) {
        sb.append(indent).append("  Blocked time: " + info.getBlockedTime()).append("\n");
        sb.append(indent).append("  Waited time: " + info.getWaitedTime()).append("\n");
    }
    if (state == java.lang.Thread.State.WAITING) {
        sb.append(indent).append("  Waiting on ").append(info.getLockName()).append("\n");
    } else if (state == java.lang.Thread.State.BLOCKED) {
        sb.append(indent).append("  Blocked on ").append(info.getLockName()).append("\n");
        sb.append(indent).append("  Blocked by ").append(org.apache.hadoop.hbase.monitoring.ThreadMonitoring.getTaskName(info.getLockOwnerId(), info.getLockOwnerName())).append("\n");
    }
    sb.append(indent).append("  Stack:").append("\n");
    for (java.lang.StackTraceElement frame : info.getStackTrace()) {
        sb.append(indent).append("    ").append(frame.toString()).append("\n");
    }
}