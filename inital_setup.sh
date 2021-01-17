#!/bin/bash
echo "This assumes you have at least python3 installed as well as a working and connected NFC HAT for the raspberry pi"
echo "This script will use a pre-built binary which will be added to /usr/local/bin"


curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
echo 'deb https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list
sudo apt update
sudo apt upgrade
sudo apt-get install -y curl apt-transport-https nodejs npm raspotify
sudo npm install -y -g pm2

echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
sudo dtparam spi=on

nodejs -v
pm2 status

cd ~/
mkdir sonos-spotify-jukebox && cd sonos-spotify-jukebox
export HOME_DIR="$(pwd)"
echo "Starting installation in $HOME_DIR"

function get_jukebox() {
  cd $HOME_DIR
  git clone https://gitlab.com/AndrewSkea/spotify-nfc-jukebox.git .
  sudo cp -f spotify-client/bin/spotify-cli /usr/local/bin
  sudo chmod +x /usr/local/bin/spotify-cli
  [ -x "$(command -v spotify-cli)" ] && echo "spotify-cli installed"
  output="$(spotify-cli devices)"
  echo "Authentication for the spotify-cli service will be done in http://localhost:8000 after reboot"
  mkdir -p $HOME_DIR/logs
}

function create_python_env() {
  cd $HOME_DIR
  python3 -m venv jukeboxenv
  source jukeboxenv/bin/activate
  pip3 install -r requirements.txt
}

function activate_env(){ 
  source $HOME_DIR/jukeboxenv/bin/activate
}


function get_sonos_http_api() {
  cd $HOME_DIR
  git clone https://github.com/jishi/node-sonos-http-api.git
}

function run_sonos_http_api() {
  cd $HOME_DIR/node-sonos-http-api
  npm install --production
  cd ..
  sudo cp -f sonosapi.service /lib/systemd/system/sonosapi.service
  sudo systemctl daemon-reload
  sudo systemctl enable sonosapi.service
  sudo systemctl start sonosapi.service
  sudo systemctl status sonosapi.service
  journalctl -u sonosapi.service
}

function start_read_service() {
  cd $HOME_DIR/read-service
  activate_env
  pm2 start Read.py --name "read-service" --log $HOME_DIR/logs/read_service.log --interpreter $HOME_DIR/jukeboxenv/bin/python
}

function start_jukebox_admin(){
  cd $HOME_DIR/jukebox-service
  sudo cp -f jukebox.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable jukebox.service
  sudo systemctl start jukebox.service
  sudo systemctl status jukebox.service
  journalctl -u jukebox.service
}

get_jukebox
create_python_env
activate_env
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
