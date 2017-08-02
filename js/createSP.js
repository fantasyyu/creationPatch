function saveTextAsFile() {
    // grab the content of the form field and place it into a variable
    //var baseImageDir = document.getElementById("txBaseImageDir").value;
    //var upgradeImageDir = document.getElementById("txUpgradeImageDir").value;
    //var changedFileList = document.getElementById("txaChangeFile").value.split("\n").join(",");
    var SPversion = document.getElementById("SPVersion").value;
    var txEmail = document.getElementById("txEmail").value;

    var patchType = $('input[name=PatchType]:checked').val()
    var strjson = {
        //'baseImageDir': baseImageDir,
        //'upgradeImageDir': upgradeImageDir,
        //'changedFileList': changedFileList,
        'SPversion': SPversion,
        'Email': txEmail,
        'PatchType': patchType
    };
    strjson.MsiGroupList = GetGroupMsiData();
    //console.log(MsiGroupList);
    var jsonse = JSON.stringify(strjson);

    //  create a new Blob (html5 magic) that conatins the data from your form feild
    //var textFileAsBlob = new Blob([textToWrite], { type: 'text/plain' });
    var textFileAsBlob = new Blob([jsonse], { type: 'application/json' });
    var d = new Date()
    var hour = d.getHours();
    var date = d.getDate();
    var month = d.getMonth() + 1;
    // Specify the name of the file to be saved
    var fileNameToSaveAs = "myconfigFile-"+month.toString()+date.toString()+hour.toString()+".json";

    // Optionally allow the user to choose a file name by providing 
    // an imput field in the HTML and using the collected data here
    // var fileNameToSaveAs = txtFileName.text;

    // create a link for our script to 'click'
    var downloadLink = document.createElement("a");
    //  supply the name of the file (from the var above).
    // you could create the name here but using a var
    // allows more flexability later.
    downloadLink.download = fileNameToSaveAs;
    // provide text for the link. This will be hidden so you
    // can actually use anything you want.
    downloadLink.innerHTML = "My Hidden Link";

    // allow our code to work in webkit & Gecko based browsers
    // without the need for a if / else block.
    window.URL = window.URL || window.webkitURL;

    // Create the link Object.
    downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
    // when link is clicked call a function to remove it from
    // the DOM in case user wants to save a second file.
    downloadLink.onclick = destroyClickedElement;
    // make sure the link is hidden.
    downloadLink.style.display = "none";
    // add the link to the DOM
    document.body.appendChild(downloadLink);

    // click the new link
    downloadLink.click();
}

function destroyClickedElement(event) {
    // remove the link from the DOM
    document.body.removeChild(event.target);
}

function loadConfigurationFile() {
    alert("loadConfigurationFile");

}

var reader = new FileReader();
reader.onload = function (e) {
    var textArea = document.getElementById("myTextArea");
    textArea.value = e.target.result;
};
//reader.readAsText(file);

function loadFile() {
    var input, file, fr;

    if (typeof window.FileReader !== 'function') {
        alert("The file API isn't supported on this browser yet.");
        return;
    }

    input = document.getElementById('fileinput');
    if (!input) {
        alert("Um, couldn't find the fileinput element.");
    }
    else if (!input.files) {
        alert("This browser doesn't seem to support the `files` property of file inputs.");
    }
    else if (!input.files[0]) {
        alert("Please select a file before clicking 'Load'");
    }
    else {
        file = input.files[0];
        fr = new FileReader();
        fr.onload = receivedText;
        fr.readAsText(file);
    }

    function receivedText(e) {
        lines = e.target.result;
        var newArr = JSON.parse(lines);

        var number = Object.keys(newArr.MsiGroupList).length;
        console.log("number is: " + number);
        
        for (i=0;i<number;i++) {
            console.log(newArr.MsiGroupList['MsiGroup' + i]);
            var newMsiGroup = newArr.MsiGroupList['MsiGroup' + i];
            console.log("baseImageDir" + i + ": " + newMsiGroup.baseImageDir);
            console.log("upgradeImageDir" + i + ": " + newMsiGroup.upgradeImageDir);
            console.log("changedFileLsit" + i + ": " + newMsiGroup.changedFileList);

            if (document.getElementById('groupMSIform' + i) == null) {
                console.log("groupMSIform" + i + "doesn't exist, start to create");
                var tmpfieldWrapper = $("<div class=\"groupMSI\" method=\"get\" id=\"groupMSIform" + i + "\"/>");
                var tmpfLegend = $("<fieldset><legend>one Group of base build msi and upgrade build msi</legend>Base Image path: <input type=\"text\" class=\"cBaseImage\" id=\"txBaseImageDir" + i + "\"/> Upgrade Image path: <input type=\"text\" class=\"cUpgradeImage\" id=\"txUpgradeImageDir" + i + "\"/>" + " Changed File List: <textarea class=\"cChangedFile\" " + "id=\"txaChangeFile" + i + "\" ></textarea>");
                var tmpremoveButton = $("<input type=\"button\" class=\"remove\" value=\"remove\" /></fieldset>");
                tmpremoveButton.click(function () {
                    $(this).parent().remove();
                });
                tmpfieldWrapper.append(tmpfLegend);
                tmpfieldWrapper.append(tmpremoveButton);
                $("#groupMSIform0").append(tmpfieldWrapper);
            }

            document.getElementById('txBaseImageDir' + i).value = newMsiGroup.baseImageDir;
            document.getElementById('txUpgradeImageDir' + i).value = newMsiGroup.upgradeImageDir;
            document.getElementById('txaChangeFile' + i).value = newMsiGroup.changedFileList;
        }
        //alert(newArr.baseImageDir + newArr.upgradeImageDir);

        //document.getElementById("txBaseImageDir").value = newArr.baseImageDir;
        //document.getElementById("txUpgradeImageDir").value = newArr.upgradeImageDir;
        //document.getElementById("txaChangeFile").value = newArr.changedFileList.split(",").join("\n");
        document.getElementById("SPVersion").value = newArr.SPversion;
        document.getElementById("txEmail").value = newArr.Email;
        console.log("PatchType: " + newArr.PatchType);
        $("input[name=PatchType][value=" + newArr.PatchType + "]").attr('checked', 'checked');
    }
}

function GetGroupMsiData() {
    console.log("ID number is: " + intId.toString());

    var GroupList = new Object();
    var tempBaseImageName, tempUpgradeImageName, tempChangeFileList;
    count = $('.groupMSI').length;
    if (intId <count)
        intId = count;
    for (i = 0, num=0; i < intId; i++) {
        tempBaseImageName = "txBaseImageDir" + i;
        tempUpgradeImageName = "txUpgradeImageDir" + i;
        tempChangeFileList = "txaChangeFile" + i;
        
        if (document.getElementById(tempBaseImageName) == null || document.getElementById(tempUpgradeImageName) == null)
            continue;
        if (document.getElementById(tempBaseImageName).value == '' || document.getElementById(tempUpgradeImageName).value == '')
            alert("The patch for base or update image is empty, please check it");

        var baseImageValue = document.getElementById(tempBaseImageName).value;
        var upgradeImageValue = document.getElementById(tempUpgradeImageName).value;
        var changedFileListValue = document.getElementById(tempChangeFileList).value;

        var newGroup = { ['MsiGroup'+num]: { ['baseImageDir']: baseImageValue, ['upgradeImageDir']: upgradeImageValue, ['changedFileList']: changedFileListValue } };
        $.extend(GroupList, newGroup);
        
        num++;
    }
    return GroupList;
}


// EOF