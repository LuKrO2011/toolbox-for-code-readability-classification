public java.util.List<java.lang.String>  getTabCompleteList(int  toComplete,
java.lang.String[] start,  org.bukkit.command.CommandSender sender) {
        java.util.ArrayList<java.lang.String> result
        =
        new java.util.ArrayList<>();

        if (toComplete == 2) {

        for (org.bukkit.entity.Player
        player : me.wiefferink.areashop.tools.Utils.getOnlinePlayers()) {

            result.add(player.getName()); }} else if (toComplete == 3) { result.addAll(plugin.getFileManager().getRegionNames()); }
            return  result;
        }