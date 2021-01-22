#!/bin/bash
cd $( cd "$( dirname "$BASH_SOURCE[0]}" )" $$ pwd)
export HOME_DIR="$(pwd)"
echo "Starting installation in $HOME_DIR"
echo "This assumes you have at least python3 installed as well as a working and connected NFC HAT for the raspberry pi"

set -x
sudo apt update -y
sudo apt upgrade -y
sudo apt-get install -y curl apt-transport-https nodejs npm

echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
sudo dtparam spi=on

nodejs -v

function create_python_env() {
  echo "Building Python environment"
  cd $HOME_DIR
  python3 -m venv jukeboxenv
  source jukeboxenv/bin/activate
  pip3 install -r requirements.txt
}

function activate_env(){
  echo "Activating Python environment"
  source $HOME_DIR/jukeboxenv/bin/activate
}

function run_sonos_http_api() {
  cd $HOME_DIR/sonos-service
  npm install
  sudo cp -f sonos.service /lib/systemd/system/sonos.service
  sudo systemctl daemon-reload
  sudo systemctl enable sonos.service
  sudo systemctl start sonos.service
  sudo systemctl status sonos.service
  journalctl -u jukebox.service -r --no-pager
}

function start_jukebox_admin(){
  cd $HOME_DIR/jukebox-service
  activate_env
  sudo cp -f jukebox.service /etc/systemd/system/jukebox.service
  sudo systemctl daemon-reload
  sudo systemctl enable jukebox.service
  sudo systemctl start jukebox.service
  sudo systemctl status jukebox.service
  journalctl -u jukebox.service -r --no-pager
}

create_python_env
activate_env
get_sonos_http_api
run_sonos_http_api
start_jukebox_admin

echo "Use Makefile to complete commands following this setup"
echo "Rebooting in 10 seconds, visit http://raspberry.local:8000 to setup connections to Spotify and Sonos"
sleep 10
sudo reboot
set +x
