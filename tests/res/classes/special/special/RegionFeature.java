public abstract class RegionFeature implements org.bukkit.event.Listener {
    public static  final me.wiefferink.areashop.AreaShop plugin =
    me.wiefferink.areashop.AreaShop.getInstance();


    public  org.bukkit.configuration.file.YamlConfiguration config = me.wiefferink.areashop.features.RegionFeature.plugin.getConfig();


    private  me.wiefferink.areashop.regions.GeneralRegion  region;

    public void setRegion(me.wiefferink.areashop.regions.GeneralRegion region) {
        this.region =
        region;
    }
     /**
     * Get the region of this feature.
     *
     * @return region of this feature, or null if generic
     */
    public
    me.wiefferink.areashop.regions.GeneralRegion getRegion()
    {

        return region; }
    /**
     * Start listening to events.
     */
    public void listen()  {
me.wiefferink.areashop.features.RegionFeature.plugin.getServer().getPluginManager().registerEvents(this, me.wiefferink.areashop.features.RegionFeature.plugin);
}
 /**
 * Destroy the feature and deregister everything.
 */

public  void
shutdownFeature() {
org.bukkit.event.HandlerList.unregisterAll(this);
shutdown();
}


/**
 * Dummy method a RegionFeature implementation can override.
 */
public void shutdown() {
}
}
