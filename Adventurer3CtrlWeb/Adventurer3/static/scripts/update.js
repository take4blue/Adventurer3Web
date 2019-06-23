function callApi(url, jsonObj, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');

    xhr.onreadystatechange = (function (myxhr) {
        return function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                callback(myxhr);
            }
        }
    })(xhr);

    xhr.send(JSON.stringify(jsonObj));
}

function getStatus() {
    var s = document.getElementById("image").src = "image.jpg?count=" + new Date().getTime();
    callApi(
        "getStatus",
        { "dummy": "dummy" },
        function (o) {
            console.log(o.responseText);
            var retJson = eval('new Object(' + o.responseText + ')');
            document.getElementById("Status").innerHTML = retJson.Status;
            document.getElementById("CurrentTempNozel").innerHTML = retJson.CurrentTempNozel;
            document.getElementById("TargetTempNozel").innerHTML = retJson.TargetTempNozel;
            document.getElementById("CurrentTempBed").innerHTML = retJson.CurrentTempBed;
            document.getElementById("TargetTempBed").innerHTML = retJson.TargetTempBed;
            document.getElementById("SdProgress").innerHTML = retJson.SdProgress;
            document.getElementById("SdMax").innerHTML = retJson.SdMax;
            if (!retJson.IsConnect) {
                // Adventurer3との接続が切れたので、display.htmlをリロードし/home.htmlに持っていく
                location.reload();
            }
            if (retJson.Status == "Building" && document.getElementById("jobstop").innerHTML == "JOB停止") {
                document.getElementById("jobstop").disabled = "";
            }
            else {
                document.getElementById("jobstop").disabled = "true";
            }
        });
}

function jobStopButton() {
    ret = confirm("Jobを停止します。よろしいですか？")
    if (ret) {
        document.getElementById("jobstop").disabled = "true";
        document.getElementById("jobstop").innerHTML = "停止中"
        callApi(
            "gcode",
            { "gcode": "M26" },
            function (o) {
                document.getElementById("jobstop").innerHTML = "JOB停止"
            }
        );
    }
}

setInterval(getStatus, 5000)
