/**
 * Returns the smallest key of given upsert keys. The rule of 'small' is an upsert key
 * represented by {@link ImmutableBitSet} has smaller cardinality or has a smaller leading
 * element when the same cardinality. E.g., '{0,1}' is smaller than '{0,1,2}' and '{0,1}' is
 * smaller than '{0,2}'.
 *
 * @param upsertKeys
 * 		input upsert keys
 * @return the smallest key
 */
@javax.annotation.Nonnull public static int[]  getSmallestKey(@javax.annotation.Nullable java.util.Set<org.apache.calcite.util.ImmutableBitSet>   upsertKeys)   { if  ((null == upsertKeys)    ||  upsertKeys.isEmpty()) {
        return   new   int[0];
    }
    return upsertKeys.stream().map(ImmutableBitSet::toArray).reduce((     k1,  k2) ->   {
        if   (k1.length  < k2.length)  {
            return k1;
        }
        if  (k1.length  ==  k2.length)   {
            for (int index   =      0;  index  < k1.length;      index++)   {
                if (k1[index] <  k2[index])   { return k1;
                }
            }
        }
        return k2;
    }).get();
}