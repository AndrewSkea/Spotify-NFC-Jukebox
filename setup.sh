echo "Install necessary packages for CLI interface"

echo "Installing Raspotify"
sudo apt-get -y install curl apt-transport-https

# Add repo and its GPG key
curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
echo 'deb https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list

# Install package
sudo apt-get update
sudo apt-get -y install raspotify

read -p 'Spotify Username: ' uservar
read -sp 'Spotify Password: ' passvar

echo "OPTIONS=\" --username $uservar --password $passvar\"" >> /etc/default/raspotify
echo "DEVICE_TYPE=\"speaker\"" >> /etc/default/raspotify

sudo service raspotify restart

echo "Finished installing raspotify"

echo "Now install spotify-cli"

cd spotify-client

echo "Building to /usr/local/bin. If this doesn't work, please run the following command with another directory and add the path you chose to your PATH variable (in ~/.bashrc):"
echo "cd spotify-client && GOBIN=<PATH_YOU_CHOSE> go install && echo \"export PATH=$PATH:<PATH_YOU_CHOSE>\" >> ~/.bashrc"
GOBIN=/usr/local/bin go install

echo "Follow these steps on your web browser:"
echo "1. Go to the developer Spotify dashboard (https://developer.spotify.com/dashboard/)
echo "2. Login (or create an account if needed) and create a new app"
echo "3. Call the app Jukebox and note down the client-id and client-secret"
echo "4. Open the Settings and put down \"http://localhost:5555\"" into the redirect-uri box
echo "5. Now enter these details: "

read -p 'Spotify Client ID: ' client_id
read -sp 'Spotify Client Secret: ' client_secret

spotify-cli config --set-app-client-id $client_id --set-app-client-secret $client_secret --set-redirect-port 5555

echo "The next command will open a browser and authenticate this command line for use with your account"
spotify-cli devices

echo "You are done!! Go to http://localhost:8000 to view the admin page or, if on another device http://raspberry.local:8000"
