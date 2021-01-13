#!/bin/bash
echo "This assumes you have at least python3 installed as well as a working and connected NFC HAT for the raspberry pi"
echo "This script will use a pre-built binary which will be added to /usr/local/bin"


curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
echo 'deb https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list
sudo apt update
sudo apt upgrade
sudo apt-get install -y curl apt-transport-https nodejs npm raspotify
sudo npm install -y -g pm2

nodejs -v
pm2 status

function get_jukebox() {
  git clone https://gitlab.com/AndrewSkea/spotify-nfc-jukebox.git
  cd spotify-nfc-jukebox
  sudo -f cp spotify-client/bin/spotify-cli /usr/local/bin
  [ -x "$(command -v spotify-cli)" ]
  output="$(spotify-cli devices)"
  echo $output
  [[ $output =~ "raspotify" ]] && echo "spotifi-cli successfull installed"
  export HOME_DIR=$(pwd)
  echo $HOME_DIR
}


function get_sonos_http_api() {
  cd $HOME_DIR
  git clone https://github.com/jishi/node-sonos-http-api.git
}


function run_sonos_http_api() {
  cd $HOME_DIR/node-sonos-http-api
  npm install --production
  pm2 start npm --name "sonos-api-service" -- start
}

function start_read_service() {
  cd $HOME_DIR/read-service
  pm2 start Read.py --name "read-service"
}

function start_jukebox_admin(){
  cd $HOME_DIR/jukebox-web
  python3 -m venv venv
  source venv/bin/activate
  pip3 install -r ../requirements.txt
  pm2 start app.py --name "jukebox-service" --interpreter $HOME_DIR/jukebox-web/venv/bin/python
}

get_jukebox
get_sonos_http_api
run_sonos_http_api
start_read_service
start_jukebox_admin

OUTPUT=$(pm2 startup systemd)
OUTPUT=$(printf '%s\n' "${OUTPUT#*command:}")
$OUTPUT
pm2 save

echo "Rebooting in 10 seconds, visit http://raspberry.local:8000 to setup connections to Spotify and Sonos"
sleep 10
sudo reboot