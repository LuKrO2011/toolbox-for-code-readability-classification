<T0, T1> org.apache.flink.api.java.operators.CrossOperator.ProjectCross<I1,
I2, org.apache.flink.api.java.tuple.Tuple2<T0, T1>>
projectTuple2() {
    org.apache.flink.api.common.typeinfo.TypeInformation<?>[] fTypes =
    extractFieldTypes(fieldIndexes);
    org.apache.flink.api.java.typeutils.TupleTypeInfo<org.apache.flink.api.java.tuple.Tuple2<T0, T1>> tType =
    new
    org.apache.flink.api.java.typeutils.TupleTypeInfo<org.apache.flink.api.java.tuple.Tuple2<T0, T1>>(fTypes);
    return new
    org.apache.flink.api.java.operators.CrossOperator.ProjectCross<I1, I2,
    org.apache.flink.api.java.tuple.Tuple2<T0, T1>>(this.ds1,
    this.ds2, this.fieldIndexes, this.isFieldInFirst, tType, this, hint);
}

/**
 * Projects a pair of crossed elements to a {@link Tuple}