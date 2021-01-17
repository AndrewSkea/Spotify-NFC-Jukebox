sonos-logs:
	journalctl -u sonos.service


jukebox-logs:
	journalctl -u jukebox.service


read-logs:
	journalctl -u read.service


restart-all:
	sudo service read restart
	sudo service sonos restart
	sudo service jukebox restart