sonos-logs:
	journalctl -ru sonos.service


jukebox-logs:
	journalctl -ru jukebox.service


read-logs:
	journalctl -ru read.service


restart-all:
	sudo service read restart
	sudo service sonos restart
	sudo service jukebox restart

activate:
	source jukeboxenv/bin/activate