/**
 * Get Extra state information of the container (SCHEDULED, LOCALIZING etc.).
 * @return Extra State information.
 */
@Private
@Unstable
public ContainerSubState getContainerSubState() {
  throw new UnsupportedOperationException(
      "subclass must implement this method");
}