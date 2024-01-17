/**
 * Creates a {@link MetricRegistries} instance using the corresponding {@link MetricRegistries}
 * available to {@link ServiceLoader} on the classpath. If no instance is found, then default
 * implementation will be loaded.
 * @return A {@link MetricRegistries} implementation.
 */
static MetricRegistries load(List<MetricRegistries> availableImplementations) {

  if (availableImplementations.size() == 1) {
    // One and only one instance -- what we want/expect
    MetricRegistries impl = availableImplementations.get(0);
    LOG.info("Loaded MetricRegistries " + impl.getClass());
    return impl;
  } else if (availableImplementations.isEmpty()) {
    try {
      return ReflectionUtils.newInstance((Class<MetricRegistries>) Class.forName(defaultClass));
    } catch (ClassNotFoundException e) {
      throw new RuntimeException(e);
    }
  } else {
    // Tell the user they're doing something wrong, and choose the first impl.
    StringBuilder sb = new StringBuilder();
    for (MetricRegistries factory : availableImplementations) {
      if (sb.length() > 0) {
        sb.append(", ");
      }
      sb.append(factory.getClass());
    }
    LOG.warn("Found multiple MetricRegistries implementations: " + sb
      + ". Using first found implementation: " + availableImplementations.get(0));
    return availableImplementations.get(0);
  }
}