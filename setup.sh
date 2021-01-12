#!/bin/bash
echo "This assumes you have at least python3 installed as well as a working and connected NFC HAT for the raspberry pi"
echo "This script will use a pre-built binary which will be added to /usr/local/bin"
echo "If you would like to re-build the spotify-client, you must have GO installed, then run the build_app.sh script in the spotify-client/ directory"

export HOME_DIR=$(pwd)
echo $HOME_DIR
export RASPOTIFY_EXISTS=1
export RASPOTIFY_CONF_SETUP=1
export RASPOTIFY_DEVICE_EXISTS=1
export SPOTIFY_CLIENT_EXISTS=1
export NFC_READ_SERVICE_EXISTS=1
export JUKEBOX_SERVICE_EXISTS=1

function output_envs() {
echo "RASPOTIFY_EXISTS=$RASPOTIFY_EXISTS"
echo "RASPOTIFY_CONF_SETUP=$RASPOTIFY_CONF_SETUP"
echo "RASPOTIFY_DEVICE_EXISTS=$RASPOTIFY_DEVICE_EXISTS"
echo "SPOTIFY_CLIENT_EXISTS=$SPOTIFY_CLIENT_EXISTS"
echo "NFC_READ_SERVICE_EXISTS=$NFC_READ_SERVICE_EXISTS"
echo "JUKEBOX_SERVICE_EXISTS=$JUKEBOX_SERVICE_EXISTS"
}


export STATUS="active"

# Check if raspotify exists and is running
if systemctl is-active --quiet jukebox ; then    
  echo "Running: jukebox service"
  export JUKEBOX_SERVICE_EXISTS=0
fi

# Check if raspotify exists and is running
if systemctl is-active --quiet raspotify; then    
  echo "Running raspotify service"
  export RASPOTIFY_EXISTS=0
fi

# Check if raspotify exists and is running
if systemctl is-active --quiet nfc_status; then    
  echo "Running: the nfc_read service"
  export NFC_READ_SERVICE_EXISTS=0
fi

# Check spotify-cli command exists
[ -x "$(command -v spotify-cli)" ] && export SPOTIFY_CLIENT_EXISTS=0

# Check if raspotify conf exists and has got a username and password
cat /etc/default/raspotify | grep '^OPTION*' && export RASPOTIFY_CONF_SETUP=0

echo "-----------------------------"
output_envs
echo "-----------------------------"

cd $HOME_DIR
echo "Checking Raspotify exists"
if [[ $RASPOTIFY_EXISTS == 1 ]]; then 
    echo "Installing Raspotify"
    sudo apt-get -y install curl apt-transport-https

    # Add repo and its GPG key
    curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
    echo 'deb https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list

    # Install package
    sudo apt-get update
    sudo apt-get -y install raspotify
fi

cd $HOME_DIR
echo "Check if raspotify conf exists"
if [[ $RASPOTIFY_CONF_SETUP == 1 ]]; then 
    read -p 'Spotify Username: ' uservar
    read -sp 'Spotify Password: ' passvar

    echo "OPTIONS=\" --username $uservar --password $passvar\"" >> /etc/default/raspotify
    echo "DEVICE_TYPE=\"speaker\"" >> /etc/default/raspotify

    sudo service raspotify restart

    echo "Finished installing raspotify"
fi


cd $HOME_DIR
echo "Checking if spotify-cli exists"
if [[ $SPOTIFY_CLIENT_EXISTS == 1 ]]; then 
    echo "Now install spotify-cli"
    cp spotify-client/bin/spotify-cli /usr/local/bin
    echo "Added spotify-cli to /usr/local/bin"
    [ -x "$(command -v spotify-cli)" ] && export SPOTIFY_CLIENT_EXISTS=0
fi

output="$(spotify-cli devices)"
echo $output
[[ $output =~ "raspotify" ]] &&  export RASPOTIFY_DEVICE_EXISTS=0

cd $HOME_DIR
echo "Checking if raspotify in list of devices: $RASPOTIFY_DEVICE_EXISTS"
if [[ $RASPOTIFY_DEVICE_EXISTS == 1 ]]; then  
    echo "Follow these steps on your web browser:"
    echo "1. Go to the developer Spotify dashboard (https://developer.spotify.com/dashboard/)"
    echo "2. Login (or create an account if needed) and create a new app"
    echo "3. Call the app Jukebox and note down the client-id and client-secret"
    echo "4. Open the Settings and put down \"http://localhost:5555\"" into the redirect-uri box
    echo "5. Now enter these details: "

    read -p 'Spotify Client ID: ' client_id
    read -sp 'Spotify Client Secret: ' client_secret

    spotify-cli config --set-app-client-id $client_id --set-app-client-secret $client_secret --set-redirect-port 5555

    echo "The next command will open a browser and authenticate this command line for use with your account"
    spotify-cli devices
fi


cd $HOME_DIR
echo "Checking if jukbox web is up"
if [[ $JUKEBOX_SERVICE_EXISTS == 1 ]]; then
    cd jukebox-web
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r ../requirements.txt

    echo "Running web service for jukebox admin"
    export APP_FILE="$HOME_DIR/jukebox-web/jukebox.service"
    envsubst < "jukebox.service.template" > "jukebox.service"
    sudo cp jukebox.service /etc/systemd/system/jukebox.service
    sudo systemctl start jukebox
fi

cd $HOME_DIR
echo "Check if NFC Read service is up"
if [[ $NFC_READ_SERVICE_EXISTS == 1 ]]; then
    echo "Create the NFC Read service"
    cd read-service/
    cp Read.py ReadProd.py
    export SPOTIFY_ENV_DIR=$HOME_DIR/jukebox-web/venv/bin/python 
    export READ_SCRIPT_PATH="$(pwd)/ReadProd.py"
    envsubst < "nfc_read.service.template" > "nfc_read.service"
    sudo cp nfc_read.service /etc/systemd/system/nfc_read.service
    sudo systemctl start nfc_read
fi


cd $HOME_DIR
echo "You are done!! Go to http://localhost:8000 to view the admin page or, if on another device http://raspberry.local:8000"
