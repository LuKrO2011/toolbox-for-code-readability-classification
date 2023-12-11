public String getHelp(CommandSender target) {
	if(target.hasPermission("areashop.addfriendall") || target.hasPermission("areashop.addfriend")) {
		return "help-addFriend";
	}
	return null;
}