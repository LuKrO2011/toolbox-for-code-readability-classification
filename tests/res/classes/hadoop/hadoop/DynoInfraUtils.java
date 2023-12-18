/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.hadoop.tools.dynamometer;

import org.apache.hadoop.thirdparty.com.google.common.base.Joiner;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.MalformedURLException;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Supplier;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.IOUtils;
import org.apache.hadoop.classification.InterfaceAudience;
import org.apache.hadoop.classification.InterfaceStability;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.CommonConfigurationKeysPublic;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hdfs.DFSUtilClient;
import org.apache.hadoop.hdfs.DistributedFileSystem;
import org.apache.hadoop.hdfs.client.BlockReportOptions;
import org.apache.hadoop.hdfs.protocol.ClientDatanodeProtocol;
import org.apache.hadoop.hdfs.protocol.DatanodeInfo;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.util.Time;
import org.apache.hadoop.yarn.YarnUncaughtExceptionHandler;
import org.apache.hadoop.yarn.api.ApplicationConstants.Environment;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import org.slf4j.Logger;


/**
 * A collection of utilities used by the Dynamometer infrastructure application.
 */
@InterfaceAudience.Private
@InterfaceStability.Unstable
public final class DynoInfraUtils {

  private DynoInfraUtils() {}

  public static final String DYNO_CONF_PREFIX = "dyno.";
  public static final String DYNO_INFRA_PREFIX = DYNO_CONF_PREFIX + "infra.";

  public static final String APACHE_DOWNLOAD_MIRROR_KEY = DYNO_CONF_PREFIX
      + "apache-mirror";
  // Set a generic mirror as the default.
  public static final String APACHE_DOWNLOAD_MIRROR_DEFAULT =
      "http://mirrors.ocf.berkeley.edu/apache/";
  private static final String APACHE_DOWNLOAD_MIRROR_SUFFIX_FORMAT =
      "hadoop/common/hadoop-%s/hadoop-%s.tar.gz";
  public static final String HADOOP_TAR_FILENAME_FORMAT = "hadoop-%s.tar.gz";

  public static final String DATANODE_LIVE_MIN_FRACTION_KEY =
      DYNO_INFRA_PREFIX + "ready.datanode-min-fraction";
  public static final float DATANODE_LIVE_MIN_FRACTION_DEFAULT = 0.99f;
  public static final String MISSING_BLOCKS_MAX_FRACTION_KEY =
      DYNO_INFRA_PREFIX + "ready.missing-blocks-max-fraction";
  public static final float MISSING_BLOCKS_MAX_FRACTION_DEFAULT = 0.0001f;
  public static final String UNDERREPLICATED_BLOCKS_MAX_FRACTION_KEY =
      DYNO_INFRA_PREFIX + "ready.underreplicated-blocks-max-fraction";
  public static final float UNDERREPLICATED_BLOCKS_MAX_FRACTION_DEFAULT = 0.01f;

  // The JMX bean queries to execute for various beans.
  public static final String NAMENODE_STARTUP_PROGRESS_JMX_QUERY =
      "Hadoop:service=NameNode,name=StartupProgress";
  public static final String FSNAMESYSTEM_JMX_QUERY =
      "Hadoop:service=NameNode,name=FSNamesystem";
  public static final String FSNAMESYSTEM_STATE_JMX_QUERY =
      "Hadoop:service=NameNode,name=FSNamesystemState";
  public static final String NAMENODE_INFO_JMX_QUERY =
      "Hadoop:service=NameNode,name=NameNodeInfo";
  // The JMX property names of various properties.
  public static final String JMX_MISSING_BLOCKS = "MissingBlocks";
  public static final String JMX_UNDER_REPLICATED_BLOCKS =
      "UnderReplicatedBlocks";
  public static final String JMX_BLOCKS_TOTAL = "BlocksTotal";
  public static final String JMX_LIVE_NODE_COUNT = "NumLiveDataNodes";
  public static final String JMX_LIVE_NODES_LIST = "LiveNodes";

  /**
   * Get the URI that can be used to access the tracking interface for the
   * NameNode, i.e. the web UI of the NodeManager hosting the NameNode
   * container.
   *
   * @param nameNodeProperties The set of properties representing the
   *                           information about the launched NameNode.
   * @return The tracking URI.
   */
  static URI getNameNodeTrackingUri(Properties nameNodeProperties)
      throws IOException {
    return URI.create(String.format("http://%s:%s/node/containerlogs/%s/%s/",
        nameNodeProperties.getProperty(DynoConstants.NN_HOSTNAME),
        nameNodeProperties.getProperty(Environment.NM_HTTP_PORT.name()),
        nameNodeProperties.getProperty(Environment.CONTAINER_ID.name()),
        UserGroupInformation.getCurrentUser().getShortUserName()));
  }

  /**
   * Get the set of properties representing information about the launched
   * NameNode. This method will wait for the information to be available until
   * it is interrupted, or {@code shouldExit} returns true. It polls for a file
   * present at {@code nameNodeInfoPath} once a second and uses that file to
   * load the NameNode information.
   *
   * @param shouldExit Should return true iff this should stop waiting.
   * @param conf The configuration.
   * @param nameNodeInfoPath The path at which to expect the NameNode
   *                         information file to be present.
   * @param log Where to log information.
   * @return Absent if this exited prematurely (i.e. due to {@code shouldExit}),
   *         else returns a set of properties representing information about the
   *         launched NameNode.
   */
  static Optional<Properties> waitForAndGetNameNodeProperties(
      Supplier<Boolean> shouldExit, Configuration conf, Path nameNodeInfoPath,
      Logger log) throws IOException, InterruptedException {
    while (!shouldExit.get()) {
      try (FSDataInputStream nnInfoInputStream = nameNodeInfoPath
          .getFileSystem(conf).open(nameNodeInfoPath)) {
        Properties nameNodeProperties = new Properties();
        nameNodeProperties.load(nnInfoInputStream);
        return Optional.of(nameNodeProperties);
      } catch (FileNotFoundException fnfe) {
        log.debug("NameNode host information not yet available");
        Thread.sleep(1000);
      } catch (IOException ioe) {
        log.warn("Unable to fetch NameNode host information; retrying", ioe);
        Thread.sleep(1000);
      }
    }
    return Optional.empty();
  }

}
