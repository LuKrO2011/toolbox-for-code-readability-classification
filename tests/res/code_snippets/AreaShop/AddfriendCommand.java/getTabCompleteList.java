public List<String> getTabCompleteList(int toComplete, String[] start, CommandSender sender) {
	ArrayList<String> result = new ArrayList<>();
	if(toComplete == 2) {
		for(Player player : Utils.getOnlinePlayers()) {
			result.add(player.getName());
		}
	} else if(toComplete == 3) {
		result.addAll(plugin.getFileManager().getRegionNames());
	}
	return result;
}