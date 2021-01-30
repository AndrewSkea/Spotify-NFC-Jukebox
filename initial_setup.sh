#!/bin/bash
set -x

export HOME_DIR=~/jukebox
mkdir -p $HOME_DIR
echo "Copying source files to $HOME_DIR so it is seperate to this git repo (so you can change this repo without affecting the service"
cp -fr src/* $HOME_DIR

echo "Starting installation in $HOME_DIR"
echo "This assumes you have at least python3 installed as well as a working and connected NFC HAT for the raspberry pi"

curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
echo 'deb https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list
sudo apt update -y
sudo apt upgrade -y
sudo apt-get install -y curl apt-transport-https nodejs npm python3-venv raspotify

echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
sudo dtparam spi=on
sudo amixer cset numid=3 <1>

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
  sudo cp -f sonos.service /etc/systemd/system/sonos.service
  sudo systemctl daemon-reload
  sudo systemctl enable sonos.service
  journalctl -u jukebox.service -r --no-pager
}

function start_jukebox_admin(){
  cd $HOME_DIR/jukebox-service
  activate_env
  sudo cp -f jukebox.service /etc/systemd/system/jukebox.service
  sudo systemctl daemon-reload
  sudo systemctl enable jukebox.service
  sudo systemctl start jukebox.service
  journalctl -u jukebox.service -r --no-pager
}

create_python_env
activate_env
run_sonos_http_api
start_jukebox_admin

sudo sed -i "s/raspberrypi/jukebox/g" /etc/hosts
sudo sed -i "s/raspberrypi/jukebox/g" /etc/hostname

FOLDER=/etc/systemd/system/getty@tty1.service.d/
sudo mkdir -p $FOLDER
echo '[Service]' | sudo tee $FOLDER/autologin.conf
echo 'ExecStart=' | sudo tee -a $FOLDER/autologin.conf
echo 'ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM' | sudo tee -a $FOLDER/autologin.conf

echo "Use Makefile to complete commands following this setup"
echo "Rebooting in 10 seconds, visit http://jukebox.local:8000 to setup connections to Spotify and Sonos"
sleep 10
sudo reboot
set +x
