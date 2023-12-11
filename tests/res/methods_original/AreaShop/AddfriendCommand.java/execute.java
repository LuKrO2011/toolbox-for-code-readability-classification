public void execute(CommandSender sender, String[] args) {
	if(!sender.hasPermission("areashop.addfriend") && !sender.hasPermission("areashop.addfriendall")) {
		plugin.message(sender, "addfriend-noPermission");
		return;
	}

	if(args.length < 2) {
		plugin.message(sender, "addfriend-help");
		return;
	}

	GeneralRegion region;
	if(args.length <= 2) {
		if(sender instanceof Player) {
			// get the region by location
			List<GeneralRegion> regions = Utils.getImportantRegions(((Player)sender).getLocation());
			if(regions.isEmpty()) {
				plugin.message(sender, "cmd-noRegionsAtLocation");
				return;
			} else if(regions.size() > 1) {
				plugin.message(sender, "cmd-moreRegionsAtLocation");
				return;
			} else {
				region = regions.get(0);
			}
		} else {
			plugin.message(sender, "cmd-automaticRegionOnlyByPlayer");
			return;
		}
	} else {
		region = plugin.getFileManager().getRegion(args[2]);
		if(region == null) {
			plugin.message(sender, "cmd-notRegistered", args[2]);
			return;
		}
	}
	if(sender.hasPermission("areashop.addfriendall")) {
		if((region instanceof RentRegion && !((RentRegion)region).isRented())
				|| (region instanceof BuyRegion && !((BuyRegion)region).isSold())) {
			plugin.message(sender, "addfriend-noOwner", region);
			return;
		}
		OfflinePlayer friend = Bukkit.getOfflinePlayer(args[1]);
		if(friend.getLastPlayed() == 0 && !friend.isOnline() && !plugin.getConfig().getBoolean("addFriendNotExistingPlayers")) {
			plugin.message(sender, "addfriend-notVisited", args[1], region);
			return;
		}
		if(region.getFriendsFeature().getFriends().contains(friend.getUniqueId())) {
			plugin.message(sender, "addfriend-alreadyAdded", friend.getName(), region);
			return;
		}
		if(region.isOwner(friend.getUniqueId())) {
			plugin.message(sender, "addfriend-self", friend.getName(), region);
			return;
		}
		if(region.getFriendsFeature().addFriend(friend.getUniqueId(), sender)) {
			region.update();
			plugin.message(sender, "addfriend-successOther", friend.getName(), region);
		}
	} else {
		if(sender.hasPermission("areashop.addfriend") && sender instanceof Player) {
			if(region.isOwner((Player)sender)) {
				OfflinePlayer friend = Bukkit.getOfflinePlayer(args[1]);
				if(friend.getLastPlayed() == 0 && !friend.isOnline() && !plugin.getConfig().getBoolean("addFriendNotExistingPlayers")) {
					plugin.message(sender, "addfriend-notVisited", args[1], region);
					return;
				}
				if(region.getFriendsFeature().getFriends().contains(friend.getUniqueId())) {
					plugin.message(sender, "addfriend-alreadyAdded", friend.getName(), region);
					return;
				}
				if(region.isOwner(friend.getUniqueId())) {
					plugin.message(sender, "addfriend-self", friend.getName(), region);
					return;
				}

				if(region.getFriendsFeature().addFriend(friend.getUniqueId(), sender)) {
					region.update();
					plugin.message(sender, "addfriend-success", friend.getName(), region);
				}
			} else {
				plugin.message(sender, "addfriend-noPermissionOther", region);
			}
		} else {
			plugin.message(sender, "addfriend-noPermission", region);
		}
	}
}