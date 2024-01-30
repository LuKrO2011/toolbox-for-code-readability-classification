private int year(int year, int centuryCode) {
    switch (centuryCode) {
        case 4 :
            return 1800 + year;
        case 0 :
            return 1900 + year;
        case 1 :
            return 2000 + year;
        case 2 :
            return 2100 + year;
        case 3 :
            return 2200 + year;
        default :
            throw new IllegalStateException("Invalid century code.");
    }
}