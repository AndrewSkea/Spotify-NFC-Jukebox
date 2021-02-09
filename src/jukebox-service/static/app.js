var aux_button_el, sonos_button_el, log_table, uri_input_box, 
update_write_box, update_read_box, state_el, artist_el, 
album_el, title_el;

function log(message) {
    console.log(message);
    var row = log_table.insertRow(0);
    var cell = row.insertCell(0);
    cell.innerHTML = message;
    if (log_table.rows.length > 10) {
        log_table.deleteRow(10);
    }
}

function alert(message, is_error){
    if (is_error){
        $.notify(message, "error");
    } else {
        $.notify(message, "success");
    }
}


$(document).ready(function() {
    uri_input_box = document.getElementById('uri_input_box');
    update_write_box = document.getElementById('update_write_box');
    update_read_box = document.getElementById('update_read_box');
    state_el = document.getElementById('state');
    title_el = document.getElementById('title');
    artist_el = document.getElementById('artist');
    album_el = document.getElementById('album');
    log_table = document.getElementById('log-table');
    toggle_play = document.getElementById('toggle-play');
    aux_button_el = document.getElementById('aux-button');
    sonos_button_el = document.getElementById('sonos-button');

    $("#write-form").submit(function(e) {
        e.preventDefault();
    });
    
    updateCurrentState()
    window.setInterval(function(){
        updateCurrentState()
    }, 3000);
    
    log("Finished Setup of page");
});

/*
  THE CHECK WRITE PROGRESS FUNCTION (READ / WRITE)
*/
function checkWriteProgress() {
        $.get('/check-write-progress', function(data) {
            if (data.status != "complete") {
                update_write_box.innerHTML = data.status
                setTimeout(checkWriteProgress, 1000)
            } else {
                if (data.cid != ""){
                    var s = "Written: " + data.uri + "<br>Card ID:" + data.cid + "<br><b>Remove card from reader</b>";
                    update_write_box.innerHTML = s;
                    log(s);
                    log("Finished Write");
                    setTimeout(clearWrite, 10000);
                } else {
                    update_write_box.innerHTML = "Time out on this function, please try again. If it fails again, reboot the Raspberry Pi."
                }
                
            }
        })
}


function checkReadProgress() {
        $.get('/check-read-progress', function(data) {
            if (data.status != "complete") {
                update_read_box.innerHTML = data.status
                setTimeout(checkReadProgress, 1000)
            } else {
                if (data.cid != ""){
                    var s = "URI: " + data.uri + "<br>Card ID:" + data.cid + "<br><b>Remove card from reader</b>";
                    update_read_box.innerHTML = s;
                    log(s);
                    log("Finished Read");
                    setTimeout(clearRead, 10000);
                } else {
                    update_read_box.innerHTML = "Time out on this function, please try again. If it fails again, reboot the Raspberry Pi."
                }
                
            }
        })
}


/*
  THE WRITING FUNCTION
*/
function startWrite() {
    var uri = uri_input_box.value
    log(uri);
    update_write_box.innerHTML = "Please wait, setting up Write Service";

    fetch("/write-uri/" + uri, {
    method: 'post',
    headers: {
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }, body: ''
    })
    .then(function (data) {
        setTimeout(checkWriteProgress, 1000);
    })
    .catch(function (error) {
    log('Request failed', error);
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


function startRead() {    
    log("Start Read progress");
    update_read_box.innerHTML = "Please wait, setting up Read Service";
    fetch("/read-uri")
    .then(res => {
    try {
        if (res.ok) {
            setTimeout(checkReadProgress, 1000);
        } else {
        throw new Error(res)
        }
    }
    catch (err) {
        log(err.message)
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
        log(err.message)
        return {"status": "Failed"}
    }
    })
    .then (resJson => {
        if (resJson["state"]){
            var title = resJson["state"]["title"];
            if (resJson["state"]["is_paused"]){
                state_el.innerHTML = "Paused";
                toggle_play.innerHTML = "Play";
            } else {
                state_el.innerHTML = "Playing";
                toggle_play.innerHTML = "Pause";
            }
            title_el.innerHTML = title;
            artist_el.innerHTML = resJson["state"]["artist"];
            album_el.innerHTML = resJson["state"]["album"];
            if (title_el.innerHTML == ""){
                title_el.innerHTML = "Nothing Playing"
            } 
        } else {
            alert("No connection to Sonos API", true)
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
        log('Request finished with JSON response', data);
        if (data["status"] == "error"){
            alert("Coudn't perform this action", true)
        } else {
            alert("Going to next song", false)
            updateCurrentState()
        }
    })
    .catch(function (error) {
        log('Request failed', error);
    });
}


function togglePlay() {
    if (toggle_play.innerHTML === "Pause"){
        pause()
    }
    if (toggle_play.innerHTML === "Play"){
        play()
    }
}


function next() {
    fetch("/next-song")
    .then(res => {
    try {
        if (res.ok) {
            updateCurrentState()
            return res.json()
        } else {
            throw new Error(res)
        }
    }
    catch (err) {
        return err;
    }
    }).catch(function (error) {
        log('Request failed', error);
    });
}


function pause() {
    fetch("/pause-song")
    .then(res => {
    try {
        if (res.ok) {
            updateCurrentState()
            return res.json()
        } else {
            throw new Error(res)
        }
    }
    catch (err) {
        return err;
    }
    }).catch(function (error) {
        log('Request failed', error);
    });
}


function changeToSonos() {
    fetch("/change-to-sonos")
    .then(res => {
    try {
        if (res.ok) {
            aux_button_el.style.display = "block";
            sonos_button_el.style.display = "none";
            alert("Changed to Sonos", false)
        } else {
            alert("Changed to Sonos failed", true)
            throw new Error(res)
        }
    }
    catch (err) {
        return err;
    }
    }).catch(function (error) {
        log('Request failed', error);
    });
}


function changeToAux() {
    fetch("/change-to-aux")
    .then(res => {
    try {
        if (res.ok) {
            aux_button_el.style.display = "none";
            sonos_button_el.style.display = "block";
            alert("Changed to AUX", false)
        } else {
            alert("Changed to AUX failed", true)
            throw new Error(res)
        }
    }
    catch (err) {
        return err;
    }
    }).catch(function (error) {
        log('Request failed', error);
    });
}


function play() {
    fetch("/play-song")
    .then(res => {
    try {
        if (res.ok) {
            updateCurrentState()
            return res.json()
        } else {
            throw new Error(res)
        }
    }
    catch (err) {
        return err;
    }
    }).catch(function (error) {
        log('Request failed', error);
    });
}
