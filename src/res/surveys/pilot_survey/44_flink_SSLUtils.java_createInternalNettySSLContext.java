/**
 * Creates the SSL Context for internal SSL, if internal SSL is configured. For internal SSL,
 * the client and server side configuration are identical, because of mutual authentication.
 */
@javax.annotation.Nullable
private static org.apache.flink.shaded.netty4.io.netty.handler.ssl.SslContext createInternalNettySSLContext(org.apache.flink.configuration.Configuration config, boolean clientMode, org.apache.flink.shaded.netty4.io.netty.handler.ssl.SslProvider
provider) throws java.lang.Exception {Preconditions.checkNotNull(config, "config"); if (!org.apache.flink.configuration.SecurityOptions.isInternalSSLEnabled(config))
{
return null;
}
java.lang.String[]  v25
= org.apache.flink.runtime.net.SSLUtils.getEnabledProtocols(config);java.util.List<java.lang.String> ciphers = java.util.Arrays.asList(org.apache.flink.runtime.net.SSLUtils.m1(config));
int sessionCacheSize = config.getInteger(org.apache.flink.configuration.SecurityOptions.SSL_INTERNAL_SESSION_CACHE_SIZE);
int sessionTimeoutMs = config.getInteger(org.apache.flink.configuration.SecurityOptions.SSL_INTERNAL_SESSION_TIMEOUT);
javax.net.ssl.KeyManagerFactory kmf = org.apache.flink.runtime.net.SSLUtils.getKeyManagerFactory(config, true, provider);
org.apache.flink.shaded.netty4.io.netty.handler.ssl.ClientAuth clientAuth =
org.apache.flink.shaded.netty4.io.netty.handler.ssl.ClientAuth.REQUIRE;final org.apache.flink.shaded.netty4.io.netty.handler.ssl.SslContextBuilder
sslContextBuilder;
if (clientMode) {
sslContextBuilder = org.apache.flink.shaded.netty4.io.netty.handler.ssl.SslContextBuilder.forClient().keyManager(kmf);} else {
sslContextBuilder = org.apache.flink.shaded.netty4.io.netty.handler.ssl.SslContextBuilder.forServer(kmf);
}
java.util.Optional<javax.net.ssl.TrustManagerFactory>
tmf = org.apache.flink.runtime.net.SSLUtils.getTrustManagerFactory(config,
true);
tmf.map(sslContextBuilder::trustManager);
return  sslContextBuilder.sslProvider(provider).protocols(v25).ciphers(ciphers).clientAuth(clientAuth).sessionCacheSize(sessionCacheSize).sessionTimeout(sessionTimeoutMs / 1000).build(); }