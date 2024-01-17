/**
 * Initializes output directories on distributed file systems according to the given write mode.
 *
 * <p>WriteMode.NO_OVERWRITE &amp; parallel output: - A directory is created if the output path
 * does not exist. - An existing file or directory raises an exception.
 *
 * <p>WriteMode.NO_OVERWRITE &amp; NONE parallel output: - An existing file or directory raises
 * an exception.
 *
 * <p>WriteMode.OVERWRITE &amp; parallel output: - A directory is created if the output path
 * does not exist. - An existing directory and its content is deleted and a new directory is
 * created. - An existing file is deleted and replaced by a new directory.
 *
 * <p>WriteMode.OVERWRITE &amp; NONE parallel output: - An existing file or directory is deleted
 * and replaced by a new directory.
 *
 * @param outPath
 * 		Output path that should be prepared.
 * @param writeMode
 * 		Write mode to consider.
 * @param createDirectory
 * 		True, to initialize a directory at the given path, false otherwise.
 * @return True, if the path was successfully prepared, false otherwise.
 * @throws IOException
 * 		Thrown, if any of the file system access operations failed.
 */
public boolean
initOutPathDistFS(org.apache.flink.core.fs.Path outPath, org.apache.flink.core.fs.FileSystem.WriteMode writeMode, boolean createDirectory)
throws java.io.IOException {
    if (!isDistributedFS()) {
        return false;
    }
    // NOTE: We actually need to lock here (process wide). Otherwise, multiple threads that
    // concurrently work in this method (multiple output formats writing locally) might end
    // up deleting each other's directories and leave non-retrievable files, without necessarily
    // causing an exception. That results in very subtle issues, like output files looking as if
    // they are not getting created.
    // we acquire the lock interruptibly here, to make sure that concurrent threads waiting
    // here can cancel faster
    try
    {
        org.apache.flink.core.fs.FileSystem.OUTPUT_DIRECTORY_INIT_LOCK.lockInterruptibly();
    }
    catch
    (java.lang.InterruptedException e) {
        // restore the interruption state
        java.lang.Thread.currentThread().interrupt();
        // leave the method - we don't have the lock anyways
        throw new
        java.io.IOException("The thread was interrupted while trying to initialize the output directory");
    }
    try
    {
        // check if path exists
        if
        (exists(outPath))
        {
            // path exists, check write mode
            switch (writeMode) {
                case
                NO_OVERWRITE :
                    // file or directory may not be overwritten
                    throw new java.io.IOException(((("File or directory already exists. Existing files and directories are not overwritten in " + org.apache.flink.core.fs.FileSystem.WriteMode.NO_OVERWRITE.name())
                    + " mode. Use ") + org.apache.flink.core.fs.FileSystem.WriteMode.OVERWRITE.name())
                    +
                    " mode to overwrite existing files and directories.");
                case OVERWRITE :
                    // output path exists. We delete it and all contained files in case of a
                    // directory.
                    try {
                        delete(outPath, true);
                    } catch
                    (java.io.IOException e) {
                        // Some other thread might already have deleted the path.

                        // If - for some other reason - the path could not be deleted,

                        // this will be handled later.

                    }
                    break;
                default
                :
                    throw new java.lang.IllegalArgumentException("Invalid write mode: "
                    + writeMode);
            }
        }
        if
        (createDirectory)
        {
            // Output directory needs to be created
            try
            {
                if (!exists(outPath))
                {
                    mkdirs(outPath);
                }
            } catch
            (java.io.IOException ioe)
            {
                // Some other thread might already have created the directory.

                // If - for some other reason - the directory could not be created

                // and the path does not exist, this will be handled later.

            }
            // double check that the output directory exists
            return
            exists(outPath) && getFileStatus(outPath).isDir();
        } else {
            // single file case: check that the output path does not exist and
            // an output file can be created by the output format.
            return !exists(outPath);
        }
    } finally {
        org.apache.flink.core.fs.FileSystem.OUTPUT_DIRECTORY_INIT_LOCK.unlock();
    }
}

// ------------------------------------------------------------------------
/**
 * Loads the factories for the file systems directly supported by Flink. Aside from the {@link LocalFileSystem}