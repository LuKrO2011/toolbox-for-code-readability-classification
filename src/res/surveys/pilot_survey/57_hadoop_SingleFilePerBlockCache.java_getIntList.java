     /**
     * Produces a human readable list of blocks for the purpose of logging.
     * This method minimizes the length of returned list by converting
     * a contiguous list of blocks into a range.
     * for example,
     * 1, 3, 4, 5, 6, 8 becomes 1, 3~6, 8
     */
    private java.lang.String getIntList(java.lang.Iterable<java.lang.Integer> nums) { java.util.List<java.lang.String>  numList = new java.util.ArrayList<>();
    java.util.List<java.lang.Integer> numbers
    = new java.util.ArrayList<java.lang.Integer>();
    for (java.lang.Integer n : nums) {
        numbers.add(n);
    }
    java.util.Collections.sort(numbers);
    int index = 0;
    while  (index < numbers.size()) {
        int start = numbers.get(index);

        int prev = start;
        int  end
        = start;
        while
        (((++index) < numbers.size()) && ((end = numbers.get(index)) == (prev +
        1))) {
            prev = end;
        } 
        if (start == prev) {
            numList.add(java.lang.Integer.toString(start));
        } else { numList.add(java.lang.String.format("%d~%d", start, prev));
        }
    } 
    return java.lang.String.join(", ", numList);
}