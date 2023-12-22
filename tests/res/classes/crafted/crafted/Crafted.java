/**
 * A manually crafted example class for method extraction.
 */
public class Crafted {

  @Override
	public String test1() {
		return "Test";
	}

	/**
	 * Some method comment
	 * @param a some parameter
	 */
	public String test2() {
		return "Test2";
	}

  /**
   * Some method comment containing a }.
   */
  private static void test3() {
    System.out.println("Test3");
  }

  /**
   * Some method comment
   */
  @SuppressWarnings("some:annotation")
  private static void test4() {
    System.out.println("Test4");
  }

  /**
   * Some method comment
   */

  private static void test5() {
    System.out.println("Test4");
  }

	/**
	 * Some method comment
	 */
  public abstract void test6();

  /**
   * Test inner interface
   */
  public interface ITest {

    /**
     * Test method.
     */
    public void test7();
  }

  /**
   * Test inner class
   */
  public class Test extends Other {

    /**
     * Test method.
     */
    public void test8() {
      System.out.println("Test8");
    }
  }

}

/**
 * Test interface
 */
public interface ITest2 {

  /**
   * Test method.
   */
  public void test9();

  /**
   * Test method.
   */
  public default void test10() {
    System.out.println("Test10");
  }
}
