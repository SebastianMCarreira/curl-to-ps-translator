const OPTIONS = [
    {
        "value": "ctp",
        "label": "cURL to PowerShell"
    },
    {
        "value": "ptc",
        "label": "PowerShell to cURL"
    }
]
var currentMode = 0;

var modeBtn = document.getElementById("mode-btn");
modeBtn.innerText = OPTIONS[currentMode].label;
var modeIn = document.getElementById("transl-mode");
modeIn.value = OPTIONS[currentMode].value;

var translIn = document.getElementById("transl-input");
var translOut = document.getElementById("transl-output");

modeBtn.addEventListener("click", (e)=>{
    if(currentMode){
        currentMode = 0;
        modeBtn.innerText = OPTIONS[currentMode].label;
        modeIn.value = OPTIONS[currentMode].value;
    }else{
        currentMode = 1;
        modeBtn.innerText = OPTIONS[currentMode].label;
        modeIn.value = OPTIONS[currentMode].value;
    }
});

document.getElementById("translate-btn").addEventListener("click", (e)=>{
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", URL_FOR_TRANSLATE+"?mode="+modeIn.value);
    xhttp.send(translIn.value);
    xhttp.onreadystatechange = () => {
        if(xhttp.readyState == 4){
            translOut.value = xhttp.responseText;
        }
    };
});