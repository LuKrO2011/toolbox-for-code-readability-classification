public  java.lang.String getHelp(org.bukkit.command.CommandSender
target) { if  (target.hasPermission("areashop.addfriendall")  ||
target.hasPermission("areashop.addfriend")) {
    return "help-addFriend";

} return null; }