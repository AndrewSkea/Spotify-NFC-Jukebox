echo "This assumes you have at least python3 installed as well as a working and connected NFC HAT for the raspberry pi"
echo "This script will use a pre-built binary which will be added to /usr/local/bin"
echo "If you would like to re-build the spotify-client, you must have GO installed, then run the build_app.sh script in the spotify-client/ directory"

export RASPOTIFY_EXISTS=1
export RASPOTIFY_CONF_SETUP=1
export RASPOTIFY_DEVICE_EXISTS=1
export SPOTIFY_CLIENT_EXISTS=1
export NFC_READ_SERVICE_EXISTS=1
export JUKEBOX_SERVICE_EXISTS=1

# Check if raspotify exists and is running
if service --status-all | grep -Fq 'jukebox'; then    
  sudo service jukebox restart
  export JUKEBOX_SERVICE_EXISTS=0
fi

# Check if raspotify exists and is running
if service --status-all | grep -Fq 'raspotify'; then    
  sudo service raspotify restart
  export RASPOTIFY_EXISTS=0
fi

# Check if raspotify exists and is running
if service --status-all | grep -Fq 'nfc_read'; then    
  sudo service nfc_read restart
  export NFC_READ_SERVICE_EXISTS=0
fi

# Check spotify-cli command exists
[ -x "$(command -v spotify-cli)" ] && export SPOTIFY_CLIENT_EXISTS=0

# Check if raspotify conf exists and has got a username and password
cat /etc/default/raspotify | grep '^OPTION*' && export RASPOTIFY_CONF_SETUP=0


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

if [[ $RASPOTIFY_CONF_SETUP == 1 ]]; then 
    read -p 'Spotify Username: ' uservar
    read -sp 'Spotify Password: ' passvar

    echo "OPTIONS=\" --username $uservar --password $passvar\"" >> /etc/default/raspotify
    echo "DEVICE_TYPE=\"speaker\"" >> /etc/default/raspotify

    sudo service raspotify restart

    echo "Finished installing raspotify"
fi

if [[ $SPOTIFY_CLIENT_EXISTS == 1 ]]; then 
    echo "Now install spotify-cli"
    cp spotify-client/bin/spotify-cli /usr/local/bin
    echo "Added spotify-cli to /usr/local/bin"
    [ -x "$(command -v spotify-cli)" ] && export SPOTIFY_CLIENT_EXISTS=0
fi

spotify-cli devices | grep "raspotify" && export RASPOTIFY_DEVICE_EXISTS=0

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

if [[ $NFC_READ_SERVICE_EXISTS == 1 ]]; then
    echo "Create the NFC Read service"
    cd nfc-handles
    cp Read.py ReadProd.py
    export READ_SCRIPT_PATH="$(pwd)/ReadProd.py"
    envsubst < "nfc_read.service.template" > "nfc_read.service"
    sudo cp /etc/systemd/system/nfc_read.service
    systemctl start nfc_read
fi

if [[ $JUKEBOX_SERVICE_EXISTS == 1]]; then
    cd ../jukebox-admin
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r ../requirements.txt

    echo "Running web service for jukebox admin"
    export APP_FILE="$(pwd)/jukebox.service"
    envsubst < "jukebox.service.template" > "jukebox.service"
    systemctl start jukebox
fi


echo "You are done!! Go to http://localhost:8000 to view the admin page or, if on another device http://raspberry.local:8000"
