var input_box, update_write_box;

$(document).ready(function() {
    
    input_box = document.getElementById('input_box');
    update_write_box = document.getElementById('update_write_box');

    $("#write-form").submit(function(e) {
        e.preventDefault();
    });

});

function checkWriteProgress(){
    fetch("/check-write-progress")
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
        update_write_box.innerHTML = resJson.status;
    return resJson.data
    })
    .catch(err => console.log(err))
}

function startWrite() {
    var uri = input_box.value
    console.log(uri);

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
    var repeater = setInterval(function () {
        if (callCount < 10) {
        checkWriteProgress();
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