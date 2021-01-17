var note, uri_input_box, update_write_box, update_read_box, cur_track_title, cur_track_artist, next_track_title, next_track_artist;

$(document).ready(function() {
    uri_input_box = document.getElementById('uri_input_box');
    update_write_box = document.getElementById('update_write_box');
    update_read_box = document.getElementById('update_read_box');
    title_el = document.getElementById('title');
    artist_el = document.getElementById('artist');
    album_el = document.getElementById('album');
    updateCurrentState()

    $("#write-form").submit(function(e) {
        e.preventDefault();
    });

    window.setInterval(function(){
        updateCurrentState()
    }, 5000);
});

function alert(message, is_error=False, _class=null){
    if (_class != null){
        $(_class).notify(message);
    } else {
        if (is_error){
            $.notify(message, "error");
        } else {
            $.notify(message, "success");
        }
    }
}

/*
  THE CHECK WRITE PROGRESS FUNCTION (READ / WRITE)
*/
function checkWriteProgress() {
    console.log("Getting Write progress");
    fetch("/check-write-progress")
    .then(res => {
    try {
        if (res.ok) {
        return res.json()
        } else {
        console.log("ERROR: " + res)
        return false;
        }
    }
    catch (err) {
        console.log(err.message);
        return true;
    }
    })
    .then (resJson => {
        if (resJson.status == "success"){
            update_write_box.innerHTML = "Written " + resJson["uri"] + " to card with ID " + resJson["id"];
            return true;
        } else {
            update_write_box.innerHTML = "Place RFID card on reader until confirmation here";
            return false;
        }
    })
    .catch(err => console.log(err))
}


/*
  THE WRITING FUNCTION
*/
function startWrite() {
    var uri = uri_input_box.value
    console.log(uri);
    update_write_box.innerHTML = "Please wait, setting up Write Service";

    fetch("/write-uri/" + uri, {
    method: 'post',
    headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }, body: ''
    })
    .then(function (data) {
        console.log('Request succeeded with JSON response', data);
        checkWriteProgress();
        var callCount = 1;
        var ret = false;
        var repeater = setInterval(function () {
          if (callCount < 30 && ret === false) {
            ret = checkWriteProgress();
            callCount += 1;
          } else {
            clearInterval(repeater);
            console.log("startWrite Done");
          }
        }, 1000);
    })
    .catch(function (error) {
    console.log('Request failed', error);
    return false;
    });

}

function clearWrite() {
    update_write_box.innerHTML = "";
    document.getElementById('uri_input_box').value = "";
}

function clearRead() {
    update_read_box.innerHTML = "";
}

/*
  THE CHECK READ FUNCTION
*/
function checkReadProgress(){
    console.log("Getting Read progress");
    fetch("/check-read-progress")
    .then(res => {
    try {
        if (res.ok) {
        return res.json()
        } else {
        console.log("ERROR: " + res)
        return false;
        }
    }
    catch (err) {
        console.log(err.message);
        return true;
    }
    })
    .then (resJson => {
        if (resJson.status == "success"){
            update_read_box.innerHTML = "Content: " + resJson["uri"] + " on card with ID " + resJson["id"];
            return true;
        } else {
            update_read_box.innerHTML = "Place RFID card on reader until confirmation here";
            return false;
        }
    })
    .catch(err => console.log(err))
}


function startRead() {    
    console.log("Start Read progress");
    update_read_box.innerHTML = "Please wiat, setting up Read Service";
    fetch("/read-uri")
    .then(res => {
    try {
        if (res.ok) {
            
            checkReadProgress();
            var callCount = 1;
            var ret = false;
            var repeater = setInterval(function () {
              if (callCount < 30 && ret === false) {
                ret = checkReadProgress();
                callCount += 1;
              } else {
                clearInterval(repeater);
                console.log("startRead Done");
              }
            }, 1000);
            
            return false;
        } else {
        throw new Error(res)
        }
    }
    catch (err) {
        console.log(err.message)
        return false;
    }
    })
}

/*
  THE GET STATE FUNCTIONS
*/
function updateCurrentState() {
    fetch("/get-current-status")
    .then(res => {
    try {
        if (res.ok) {
        return res.json()
        } else {
        throw new Error(res)
        }
    }
    catch (err) {
        console.log(err.message)
        return {"status": "Failed"}
    }
    })
    .then (resJson => {
        if (resJson["state"]){
            title_el.innerHTML = resJson["state"]["title"];
            artist_el.innerHTML = resJson["state"]["artist"];
            album_el.innerHTML = resJson["state"]["album"];
            if (cur_track_title.innerHTML == ""){
                cur_track_title.innerHTML = "Nothing Playing"
            } 
        } else {
            alert("No connection to Sonos API", true, ".cur_playing")
        }
    return resJson.data
    })
}

/*
  THE NEXT SONG FUNCTIONS
*/
function nextSong() {
    fetch("/next-song", {
    method: 'post',
    headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }, body: ''
    })
    .then(function (data) {
        console.log('Request finished with JSON response', data);
        if (data["status"] == "error"){
            alert("Coudn't perform this action", true)
        } else {
            alert("Going to next song", false)
            updateCurrentState()
        }
    })
    .catch(function (error) {
        console.log('Request failed', error);
    });

}

