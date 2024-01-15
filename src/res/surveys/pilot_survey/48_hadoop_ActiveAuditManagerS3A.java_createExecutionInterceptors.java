     /**
     * Return a list of execution interceptors for the AWS SDK which
     * relays to this class.
     *
     * @return a list of execution interceptors.
     */ @java.lang.Override
    public java.util.List<software.amazon.awssdk.core.interceptor.ExecutionInterceptor>  createExecutionInterceptors()   throws   java.io.IOException { // wire up the AWS SDK To call back into this class when
        // preparing to make S3 calls.
        java.util.List<software.amazon.awssdk.core.interceptor.ExecutionInterceptor> executionInterceptors =   new java.util.ArrayList<>();
        executionInterceptors.add(this);
        final  java.lang.String  handlers =   getConfig().getTrimmed(org.apache.hadoop.fs.s3a.audit.S3AAuditConstants.AUDIT_REQUEST_HANDLERS, "");
        if (!handlers.isEmpty()) {
            // warn and ignore v1 handlers.
            org.apache.hadoop.fs.s3a.impl.V2Migration.v1RequestHandlersUsed(handlers);
        }
        // V2 SDK supports global/service interceptors, but they need to be configured on the
        // classpath and don't get the filesystem/job configuration passed down.
        final  java.lang.Class<?>[] interceptors = getConfig().getClasses(org.apache.hadoop.fs.s3a.audit.S3AAuditConstants.AUDIT_EXECUTION_INTERCEPTORS);
        if  (interceptors  != null) {
            for   (java.lang.Class<?>  handler   :    interceptors)      {
                try  {
                    org.apache.hadoop.fs.s3a.audit.impl.ActiveAuditManagerS3A.LOG.debug("Adding intercept of class {}",  handler);
                    java.lang.reflect.Constructor<?>     ctor =     handler.getConstructor();
                    final software.amazon.awssdk.core.interceptor.ExecutionInterceptor interceptor  = ((software.amazon.awssdk.core.interceptor.ExecutionInterceptor)   (ctor.newInstance()));
                    if (interceptor  instanceof     org.apache.hadoop.conf.Configurable) { // pass in the configuration.
                        ((org.apache.hadoop.conf.Configurable) (interceptor)).setConf(getConfig()); }
                    executionInterceptors.add(interceptor); }  catch (java.lang.ExceptionInInitializerError      e)   {
                    throw org.apache.hadoop.util.functional.FutureIO.unwrapInnerException(e);
                } catch (java.lang.Exception  e) { throw new      java.io.IOException(e);
                }
            }
        }
        return  executionInterceptors; }