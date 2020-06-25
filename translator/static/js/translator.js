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
var translInHidd = document.getElementById("transl-input-hidd");
var translOut = document.getElementById("transl-output");
var translOutHidd = document.getElementById("transl-output-hidd");

var reportContent = document.getElementById("report-content");

var modal = document.getElementById("modal");
var modalTransIn = document.getElementById("original-code");
var modalTransInLabel = document.getElementById("original-code-label");
var modalTransOut = document.getElementById("translation-code");
var modalTransOutLabel = document.getElementById("translation-code-label");

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
            translInHidd.value = translIn.value;
            translOutHidd.value = xhttp.responseText;
        }
    };
});

document.getElementById("open-report-btn").addEventListener("click", (e)=>{
    modal.style.display = 'flex';
    modalTransIn.innerHTML = translInHidd.value;
    modalTransOut.innerHTML = translOutHidd.value;
    if(modeIn.value == 'ctp'){
        modalTransInLabel.innerHTML = "Curl";
        modalTransOutLabel.innerHTML = "Powershell";
    }else{
        modalTransInLabel.innerHTML = "Powershell";
        modalTransOutLabel.innerHTML = "Curl";
    }
});

document.getElementById("close-report-btn").addEventListener("click", (e)=>{
    modal.style.display = 'none';
});

document.getElementById("report-btn").addEventListener("click", (e)=>{
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", URL_FOR_REPORT);
    var report = {
        'mode': modeIn.value,
        'original': translInHidd.value,
        'translated': translOutHidd.value,
        'report': reportContent.value
    }
    xhttp.setRequestHeader('Content-Type','application/json');
    xhttp.send(JSON.stringify(report));
    xhttp.onreadystatechange = () => {
        if(xhttp.readyState == 4){
            alert(xhttp.responseText);
            modal.style.display = 'none';
        }
    };
});