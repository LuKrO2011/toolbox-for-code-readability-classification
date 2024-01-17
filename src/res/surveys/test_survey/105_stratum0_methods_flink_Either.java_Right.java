/** Create a Right value of Either */
public static <L, R> Either<L, R> Right(R value) {
    return new Right<L, R>(value);
}