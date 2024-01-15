                            /**
                             * Choose an access policy.
                             *
                             * @param name
                             * 		strategy name from a configuration option, etc.
                             * @param defaultPolicy
                             * 		default policy to fall back to.
                             * @return the chosen strategy
                             */
                            public static org.apache.hadoop.fs.s3a.S3AInputPolicy getPolicy(java.lang.String name, @javax.annotation.Nullable
                            org.apache.hadoop.fs.s3a.S3AInputPolicy defaultPolicy) {
                        java.lang.String trimmed = name.trim().toLowerCase(java.util.Locale.ENGLISH);
                        switch (trimmed) {
                            case OpenFileOptions.FS_OPTION_OPENFILE_READ_POLICY_ADAPTIVE :
                    case OpenFileOptions.FS_OPTION_OPENFILE_READ_POLICY_DEFAULT :
                        case Constants.INPUT_FADV_NORMAL :
                                                return org.apache.hadoop.fs.s3a.S3AInputPolicy.Normal;
                                                // all these options currently map to random IO.
                                            case OpenFileOptions.FS_OPTION_OPENFILE_READ_POLICY_RANDOM :
                                    case OpenFileOptions.FS_OPTION_OPENFILE_READ_POLICY_VECTOR :
                                return org.apache.hadoop.fs.s3a.S3AInputPolicy.Random;
                            case OpenFileOptions.FS_OPTION_OPENFILE_READ_POLICY_SEQUENTIAL :
                        case OpenFileOptions.FS_OPTION_OPENFILE_READ_POLICY_WHOLE_FILE :
                                return org.apache.hadoop.fs.s3a.S3AInputPolicy.Sequential;
                                    default :
                                            return defaultPolicy;
                                    }
                            }