var express = require('express');
var app = express();
var fs = require("fs");
const Sonos = require('sonos').Sonos
const Regions = require('sonos').SpotifyRegion
const sonos = new Sonos('192.168.0.14')
sonos.setSpotifyRegion(Regions.EU)

app.get('/play/:spotifyURI', function (req, res) {
  console.log(req.params);
  var spotifyURI = req.params.spotifyURI;
  sonos.play(spotifyURI)
  .then(success => {
    console.log('Playing: ' + spotifyURI);
    return sonos.currentTrack()
  })
  .then(track => {
    console.log(JSON.stringify(track, null, 2))
  })
  .catch(err => { console.log('Error occurred %j', err) })
})


app.get('/pause', function (req, res) {
  console.log('Paused');
  sonos.pause().then(success => {
    console.log('Paused')
    res.send("Paused");
    }).catch(err => { console.log('Error occurred %j', err) })
})


var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Sonos API application listening at http://%s:%s", host, port)
})
