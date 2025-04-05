let mediaRecorder;
let audioChunks = [];

document.getElementById("recordBtn").addEventListener("click", startRecording);
document.getElementById("stopBtn").addEventListener("click", stopRecording);

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            document.getElementById("audioPlayback").src = URL.createObjectURL(audioBlob);

            sendAudioToServer(audioBlob);
        };

        mediaRecorder.start();
        document.getElementById("recordBtn").disabled = true;
        document.getElementById("stopBtn").disabled = false;
    });
}

function stopRecording() {
    mediaRecorder.stop();
    document.getElementById("recordBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;
}

function uploadAudio() {
    const fileInput = document.getElementById("audioFile");
    if (fileInput.files.length === 0) {
        alert("Please select an audio file.");
        return;
    }

    sendAudioToServer(fileInput.files[0]);
}

function sendAudioToServer(audioBlob) {
    let formData = new FormData();
    formData.append("audio_file", audioBlob);

    fetch("/transcribe/", { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        if (data.result) {
            document.getElementById("transcriptionText").innerText = `${data.result}`;
        } else {
            document.getElementById("transcriptionText").innerText = "Error transcribing audio.";
        }
    })
    .catch(error => console.error("Error:", error));
}