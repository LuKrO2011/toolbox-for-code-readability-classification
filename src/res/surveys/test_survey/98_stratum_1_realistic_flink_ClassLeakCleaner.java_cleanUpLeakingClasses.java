    /**
     * Clean up the soft references of the classes under the specified class loader.
     */
    public static synchronized void
    cleanUpLeakingClasses(java.lang.ClassLoader classLoader)
    throws java.lang.ReflectiveOperationException,  java.lang.SecurityException, java.lang.ClassCastException {

    if (!org.apache.flink.streaming.api.utils.ClassLeakCleaner.f0) {



java.lang.Class<?> v0 =
java.lang.Class.forName("java.io.ObjectStreamClass$Caches"); org.apache.flink.streaming.api.utils.ClassLeakCleaner.clearCache(v0,  "localDescs", classLoader);

org.apache.flink.streaming.api.utils.ClassLeakCleaner.clearCache(v0, "reflectors", classLoader); 
// class loader even after job finished.

// so, trigger garbage collection explicitly to:





java.lang.System.gc();org.apache.flink.streaming.api.utils.ClassLeakCleaner.f0  = true;}
}