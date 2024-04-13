let voterList = [];
function vote(id) {
    let vorterRaw = document.getElementById('i1').value;
    let voter = vorterRaw.toLowerCase();
    if (!voter) {
        alert("Please enter your name before voting!!");
        return false;
    } else if (voterList.includes(voter)) {
        alert("You already voted. Thank You!!");
        return false;
    }
    voterList.push(voter);
    let votes = document.getElementById(id).innerHTML;
    let votesInNumber = parseInt(votes) + 1;
    alert(voter + " voted for " + id);
    document.getElementById(id).innerHTML = votesInNumber;
}

function showHideResult() {
    let resultDivID = document.getElementById('resultID');
    let divDisplaySetting = resultDivID.style.display;
    let buttonID = document.getElementById('resultButton');
    if (divDisplaySetting == 'block') {
        resultDivID.style.display = 'none';
        buttonID.innerHTML = 'Show Result';
    }
    else {
        resultDivID.style.display = 'block';
        buttonID.innerHTML = 'Hide Result';
    }
}

function clearVotingStats() {
    document.getElementById('BJP').innerHTML = "0";
    document.getElementById('Congress').innerHTML = "0";
    document.getElementById('AAP').innerHTML = "0";
    document.getElementById('ShivSena').innerHTML = "0";
    document.getElementById('NCP').innerHTML = "0";
}
