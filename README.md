# Spotify NFC Jukebox 

Disclaimer: Project still in progress

### About 
This runs a service (on a raspberry pi for example) that listens for NFC cards which have spotify URI written to them. On contact with a connected NFC Reader, it will play your Spotify URI (playlist, track or album) to a Sonos player, or out through the AUX jack (tbc).

Visit the dashbaord from another device connected to your network, after the setup below, at http://raspberry.local:8000 to finish the installation and provide the necessary authentication for the service to work.


### Setup
On a raspberry pi, connect to the internet and then run the following command
```
curl -s -L https://gitlab.com/AndrewSkea/spotify-nfc-jukebox/initial_setup.sh | bash
```

### Credit
Note this project is dependant on other projects and all likes/comments/issues related to their services should be brought up with them and I would like to say well done and thank you for such great open source work on their part!

* Sonos Controller: https://github.com/jishi/node-sonos-http-api
* Spotify CLI: https://github.com/ledesmablt/spotify-cli
* Spotify Connect Manager: https://github.com/dtcooper/raspotify
