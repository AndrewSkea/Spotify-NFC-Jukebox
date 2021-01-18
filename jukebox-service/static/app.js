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
    function worker() {
        $.get('/check-write-progress', function(data) {
            if (data.status != "complete") {
                update_write_box.innerHTML = data.status
                setTimeout(worker, 1000)
            } else {
                if (data.cid != ""){
                    update_write_box.innerHTML = "Written " + data.uri + " to card with ID " + data.cid;
                } else {
                    update_write_box.innerHTML = "Time out on this function, please try again. If it fails again, reboot the Raspberry Pi."
                }
                
            }
        })
    }
}


function checkWriteProgress() {
    function worker() {
        $.get('/check-read-progress', function(data) {
            if (data.status != "complete") {
                update_read_box.innerHTML = data.status
                setTimeout(worker, 1000)
            } else {
                if (data.cid != ""){
                    update_read_box.innerHTML = "Written " + data.uri + " to card with ID " + data.cid;
                } else {
                    update_read_box.innerHTML = "Time out on this function, please try again. If it fails again, reboot the Raspberry Pi."
                }
                
            }
        })
    }
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
        checkWriteProgress();
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


function startRead() {    
    console.log("Start Read progress");
    update_read_box.innerHTML = "Please wait, setting up Read Service";
    fetch("/read-uri")
    .then(res => {
    try {
        if (res.ok) {
            checkReadProgress();
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
            if (title_el.innerHTML == ""){
                title_el.innerHTML = "Nothing Playing"
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

