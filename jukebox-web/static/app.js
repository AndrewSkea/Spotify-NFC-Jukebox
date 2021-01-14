var note, uri_input_box, update_write_box, update_read_box, cur_track_title, cur_track_artist, next_track_title, next_track_artist;

$(document).ready(function() {
    uri_input_box = document.getElementById('uri_input_box');
    update_write_box = document.getElementById('update_write_box');
    update_read_box = document.getElementById('update_read_box');
    cur_track_title = document.getElementById('cur_track_title');
    cur_track_artist = document.getElementById('cur_track_artist');
    next_track_title = document.getElementById('next_track_title');
    next_track_artist = document.getElementById('next_track_artist');
    note = document.getElementById("note");

    $("#write-form").submit(function(e) {
        e.preventDefault();
    });

    window.setInterval(function(){
        updateCurrentState()
    }, 5000);
});

function alert(message, is_error=False){
 if (is_error){
    $.notify(message, "error");
 } else {
    $.notify(message, "success");
 }
}

/*
  THE CHECK NFC PROGRESS FUNCTION (READ / WRITE)
*/
function checkNFCProgress(box_to_update){
    fetch("/check-nfc-progress")
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
        box_to_update.innerHTML = resJson.status;
    return resJson.data
    })
    .catch(err => console.log(err))
}


/*
  THE WRITING FUNCTION
*/
function startWrite() {
    var uri = uri_input_box.value
    console.log(uri);

    fetch("/write-uri/" + uri, {
    method: 'post',
    headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }, body: ''
    })
    .then(function (data) {
    console.log('Request succeeded with JSON response', data);

    checkNFCProgress(update_write_box);
    var callCount = 1;
    var repeater = setInterval(function () {
        if (callCount < 10) {
        checkNFCProgress(update_write_box);
        callCount += 1;
        } else {
        clearInterval(repeater);
        }
    }, 1000);
    })
    .catch(function (error) {
    console.log('Request failed', error);
    });

}


/*
  THE READING FUNCTIONS
*/
function startRead() {
    var uri = input_box.value
    console.log(uri);

    fetch("/read-uri", {
    method: 'get',
    headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }})
    .then(function (data) {
        console.log('Request succeeded with JSON response', data);

        checkNFCProgress(update_read_box);
        var callCount = 1;
        var repeater = setInterval(function () {
            if (callCount < 10) {
            checkNFCProgress(update_read_box);
            callCount += 1;
            } else {
            clearInterval(repeater);
            }
        }, 1000);
    })
    .catch(function (error) {
        console.log('Request failed', error);
    });

}

/*
  THE GET STATE FUNCTIONS
*/
function updateCurrentState() {
    fetch("/get-current-status", {
    method: 'get',
    headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }})
    .then(function (data) {
        console.log('Request succeeded with JSON response', data);
        cur_track_title.innerHTML = data["state"]["cur_playing_title"];
        cur_track_artist.innerHTML = data["state"]["cur_track_artist"];
        next_track_title.innerHTML = data["state"]["next_track_title"];
        next_track_artist.innerHTML = data["state"]["next_track_artist"];
    })
    .catch(function (error) {
        console.log('Request failed', error);
    });
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

