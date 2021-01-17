var express = require('express');
var app = express();
var fs = require("fs");
const Son = require('sonos')
const Sonos = require('sonos').Sonos
const Regions = require('sonos').SpotifyRegion
const discovery = new Son.AsyncDeviceDiscovery()
var sonos;


app.get('/play/:spotifyURI', function (req, res) {
  console.log(req.params);
  var spotifyURI = req.params.spotifyURI;
  sonos.play(spotifyURI)
  .then(success => {
    console.log('Playing: ' + spotifyURI);
    res.send(sonos.currentTrack());
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


app.get('/state', function (req, res) {
  console.log('State');
  sonos.currentTrack().then(track => {
    console.log('Got current track %j', track)
    res.send(JSON.stringify(track, null, 2));
  }).catch(err => { console.log('Error occurred %j', err) })
})


app.get('/next', function (req, res) {
  sonos.next()
  .then(success => {
    console.log('Playing: ' + spotifyURI);
    return sonos.currentTrack()
  })
  .then(track => {
    console.log(JSON.stringify(track, null, 2))
  })
  .catch(err => { console.log('Error occurred %j', err) })
})


app.get('/devices', function (req, res) {
  discovery.discover().then((device, model) => {
    console.log('Found one sonos device %s getting all groups', device.host)
    return device.getAllGroups().then((groups) => {
      var group_list = [];
      for(var i = 0; i < groups.length; i++) {
          var obj = groups[i];
          group_list.push(obj.Name);
      }
      console.log(group_list);
      res.send(group_list);
    })
  }).catch(e => {
    console.warn(' Error in discovery %j', e)
  })
})


var server = app.listen(8081, function () {
  discovery.discover().then((device, model) => {
    console.log('Found one sonos device %s getting all groups', device.host)
    return device.getAllGroups().then((groups) => {
      console.log(JSON.stringify(groups, null, 2))
      console.log("HOST: " + groups[0]["host"])
      sonos = new Sonos(process.env.SONOS_NAME || groups[0]["host"])
      sonos.setSpotifyRegion(Regions.EU)
      return groups[0]
    })
  }).catch(e => {
    console.warn(' Error in discovery %j', e)
  });

   var host = server.address().address
   var port = server.address().port
   console.log("Sonos API application listening at http://%s:%s", host, port)
})
