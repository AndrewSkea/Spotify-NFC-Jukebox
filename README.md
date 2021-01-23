# Spotify NFC Jukebox 

!! WARNING !!
THIS WILL RESET YOUR HOSTNAME (to jukebox) AND AUTOLOGIN FILE (to autologin with pi user)
GO THROUGH THE INITIAL_SETUP.SH SCRIPT TO ENSURE YOU UNDERSTAND THE CHANGES BEING MADE

Disclaimer: Project still in progress (please fork and open PRs to suggest improvements)

## About
Bring back the touch and feel of a record player with this modern take on it using a Raspberry Pi and an NFC reader.

Installation runs three services:
1. Read service (spawned by jukebox service) - This listens for NFC cards and plays spotify playlist/album/tracks whilst the NFC card remains on the reader.
2. Sonos Controller Service - Based on the request, this can control the sonos players in your house.
3. Jukebox Dashboard - This provides an interface to write new cards, read current ones, update the default sonos player and see what's currently playing.

## Setup
On a raspberry pi, connect to the internet and then run the following command
```
git clone https://gitlab.com/AndrewSkea/spotify-nfc-jukebox.git
cd spotify-nfc-jukebox
. ./inital_setup.sh
```
Once you have run the inital_setup.sh script to install the services. These will run on boot so don't worry about turning you raspberry pi off then on again.

Once installed, you can visit the dashbaord from another device connected to your network, after the setup below, at http://jukebox.local:8000 (or whatever ip address your raspberry pi is on), update the Sonos player name to the one you want to play from. Then, start writing some cards!

## Writing to a card
To Write a card, input a uri from the Spotify Web Player. For example
```
with a playlist url of: https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF
the URI would be: spotify:playlist:37i9dQZEVXbMDoHDwVN2tF

with an album url of: https://open.spotify.com/album/3VWrUk4vBznMYXGMPc7dRB
the URI would be: spotify:album:3VWrUk4vBznMYXGMPc7dRB

with a track url of: https://open.spotify.com/track/2OBofMJx94NryV2SK8p8Zf
the URI would be: spotify:track:2OBofMJx94NryV2SK8p8Zf
```
Click on Write button and then place your card next to the reader (no other card should be there at the same time). Once it comes up with the message saying it has been written, remove your card from the reader.


## Reading from a card
To Read from a card, click on the Read button and then place your card next to the reader (no other card should be there at the same time). Wait until it comes up with the information from that card. Once it has, remove your card from the reader. If left on, it could start trying to play whatever is saved there.



## Credit
Note this project is dependant on other projects and all likes/comments/issues related to their services should be brought up with them and I would like to say well done and thank you for such great open source work on their part!

* Sonos Controller: https://github.com/bencevans/node-sonos
