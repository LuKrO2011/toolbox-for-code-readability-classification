public void
execute(org.bukkit.command.CommandSender
sender, java.lang.String[]  args) {if ((!sender.hasPermission("areashop.addfriend"))
    && (!sender.hasPermission("areashop.addfriendall"))) {
        plugin.message(sender,  "addfriend-noPermission");return;
    }
    if
    (args.length <
    2) { plugin.message(sender, "addfriend-help");

return;
}
me.wiefferink.areashop.regions.GeneralRegion region; if
(args.length <=
2)
{
        if (sender
        instanceof
        org.bukkit.entity.Player) {
            // get the region by location
            java.util.List<me.wiefferink.areashop.regions.GeneralRegion> regions  =
            me.wiefferink.areashop.tools.Utils.getImportantRegions(((org.bukkit.entity.Player) (sender)).getLocation());
            if (regions.isEmpty())  {
                plugin.message(sender, "cmd-noRegionsAtLocation");
                return;
            } else if
            (regions.size()  > 1)
            { plugin.message(sender,
                    "cmd-moreRegionsAtLocation");
                    return;

                } else
                { region = regions.get(0);

                    }}
                else {plugin.message(sender, "cmd-automaticRegionOnlyByPlayer"); return;
                }

        } else
        {
            region =
            plugin.getFileManager().getRegion(args[2]);if  (region == null)  {

                plugin.message(sender, "cmd-notRegistered", args[2]); return;
                }
                    }if (sender.hasPermission("areashop.addfriendall"))
                    { if
                            (((region
                            instanceof me.wiefferink.areashop.regions.RentRegion)
                            && (!((me.wiefferink.areashop.regions.RentRegion) (region)).isRented()))
                            || ((region  instanceof me.wiefferink.areashop.regions.BuyRegion) && (!((me.wiefferink.areashop.regions.BuyRegion) (region)).isSold()))) {
                            plugin.message(sender, "addfriend-noOwner", region);

                            return;}
                        org.bukkit.OfflinePlayer
                        friend  = org.bukkit.Bukkit.getOfflinePlayer(args[1]);

                        if (((friend.getLastPlayed() ==
                        0)  && (!friend.isOnline())) && (!plugin.getConfig().getBoolean("addFriendNotExistingPlayers"))) {plugin.message(sender, "addfriend-notVisited",
                        args[1], region);return;} if (region.getFriendsFeature().getFriends().contains(friend.getUniqueId())) { plugin.message(sender, "addfriend-alreadyAdded", friend.getName(), region);
                return;}

            if (region.isOwner(friend.getUniqueId())) {

                plugin.message(sender,
                "addfriend-self", friend.getName(), region);
                return;}
                    if
                    (region.getFriendsFeature().addFriend(friend.getUniqueId(), sender))
                    {region.update();

                            plugin.message(sender,  "addfriend-successOther",  friend.getName(), region);
                    }
                        } else if
                        (sender.hasPermission("areashop.addfriend") && (sender instanceof org.bukkit.entity.Player)) { if (region.isOwner(((org.bukkit.entity.Player) (sender)))) {

                            org.bukkit.OfflinePlayer friend  = org.bukkit.Bukkit.getOfflinePlayer(args[1]);
                            if
                            (((friend.getLastPlayed()  == 0) && (!friend.isOnline()))
                            && (!plugin.getConfig().getBoolean("addFriendNotExistingPlayers"))) {
                        plugin.message(sender, "addfriend-notVisited",
                        args[1], region);
                        return;
                    }
                    if (region.getFriendsFeature().getFriends().contains(friend.getUniqueId())) {plugin.message(sender,
                        "addfriend-alreadyAdded",  friend.getName(),  region);

                        return;
                    }if
                    (region.isOwner(friend.getUniqueId())) {
                        plugin.message(sender,
                        "addfriend-self",  friend.getName(),  region); return; }

                    if (region.getFriendsFeature().addFriend(friend.getUniqueId(), sender))
                    {

                            region.update();plugin.message(sender,  "addfriend-success", friend.getName(), region);}} else { plugin.message(sender, "addfriend-noPermissionOther",  region);}

                                } else {
                                    plugin.message(sender, "addfriend-noPermission", region); }
                            }