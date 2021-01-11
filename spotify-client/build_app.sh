echo "Building to /usr/local/bin. If this doesn't work, please run the following command with another directory and add the path you chose to your PATH variable (in ~/.bashrc):"
echo "cd spotify-client && GOBIN=<PATH_YOU_CHOSE> go install && echo \"export PATH=$PATH:<PATH_YOU_CHOSE>\" >> ~/.bashrc"
GOBIN=/usr/local/bin go install
