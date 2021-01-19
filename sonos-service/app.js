var express = require('express');
var app = express();
var fs = require("fs");
let jsonData = require('../config/settings.json');

const Son = require('sonos')
const Sonos = require('sonos').Sonos
const Regions = require('sonos').SpotifyRegion;
const { group } = require('console');
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
  .catch(err => { res.send('Error occurred %j', err) })
})


app.get('/pause', function (req, res) {
  console.log('Paused');
  sonos.pause().then(success => {
    console.log('Paused')
    res.send("Success");
    }).catch(err => { res.send('Error occurred %j', err) })
})


app.get('/state', function (req, res) {
  console.log('State');
  sonos.currentTrack().then(track => {
    console.log('Got current track %j', track)
    sonos.getCurrentState().then(state => {
      console.log('Got current state %j', state)
      var data = {
        "playing": track,
        "state": state
      }
      res.send(JSON.stringify(data, null, 2));
    }).catch(err => { res.send('Error occurred %j', err) })
  }).catch(err => { res.send('Error occurred %j', err) })
})

app.get('/state', function (req, res) {
  console.log('State');
  sonos.getCurrentState().then(state => {
    console.log('Got current track %j', state)
    res.send(JSON.stringify(state, null, 2));
  }).catch(err => { res.send('Error occurred %j', err) })
})


app.get('/shuffle', function (req, res) {
  console.log('Shuffle');
  sonos.setPlayMode('SHUFFLE').then(success => {
    console.log('Got current track %j', track)
    res.send("Success");
  }).catch(err => { res.send('Error occurred %j', err) })
})


app.get('/next', function (req, res) {
  sonos.next()
  .then(success => {
    return sonos.currentTrack()
  })
  .then(track => {
      sonos.play()
      .then(success => {
        res.send(JSON.stringify(track, null, 2));
      })
      .catch(err => { res.send('Error occurred %j', err) })
  })
  .catch(err => { res.send('Error occurred %j', err) })
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
  console.log("Wanted room name: " + jsonData.sonos_room);
  discovery.discover().then((device, model) => {
    console.log('Found one sonos device %s getting all groups', device.host)
    return device.getAllGroups().then((groups) => {
      var ip_add = groups[0]["host"];
      console.log("Default will be: " + groups[0].Name)
      if (jsonData.sonos_room != "") {
        groups.forEach(group => {
          if (group.Name === jsonData.sonos_room){
              console.log("Using: " + group.Name)
              ip_add = group.host;
          }
        });
      }
      console.log("Using ip address: " + ip_add)
      sonos = new Sonos(ip_add)
      sonos.setSpotifyRegion(Regions.EU)
      return ip_add
    })
  })
  .catch(e => {
    console.warn(' Error in discovery %j', e)
  });

   var host = server.address().address
   var port = server.address().port
   console.log("Sonos API application listening at http://%s:%s", host, port)
})
