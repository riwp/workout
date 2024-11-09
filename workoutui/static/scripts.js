// Check if browser supports getUserMedia for audio recording
async function startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Your browser does not support audio recording.");
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            saveRecording(audioBlob);
        };

        mediaRecorder.start();
        document.getElementById("recordButton").onclick = () => mediaRecorder.stop();
    } catch (error) {
        console.error("Error starting recording:", error);
    }
}

// Function to send audio recording to the server
function saveRecording(audioBlob) {
    const fileInput = document.getElementById("file_name");
    const descriptionInput = document.getElementById("description");
    const categoryInput = document.getElementById("category");

    if (!fileInput.value || !descriptionInput.value || !categoryInput.value) {
        alert("Please fill out all fields before saving.");
        return;
    }

    const formData = new FormData();
    formData.append("audio", audioBlob, `${fileInput.value}.wav`);
    formData.append("file_name", fileInput.value);
    formData.append("description", descriptionInput.value);
    formData.append("category", categoryInput.value);

    fetch("/record", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || "Recording saved successfully!");
    })
    .catch(error => console.error("Error saving recording:", error));
}

// Function to filter audio files by category on the Organize Workout page
function filterAudioByCategory(category) {
    const files = document.querySelectorAll(".audio-file");

    files.forEach(file => {
        if (category === "all" || file.dataset.category === category) {
            file.style.display = "block";
        } else {
            file.style.display = "none";
        }
    });
}

// Function to play audio files in sequence for a selected workout
async function playWorkout(fileList) {
    for (let file of fileList) {
        await playAudio(file);
    }
    alert("Workout complete!");
}

// Helper function to play a single audio file and wait for it to finish
function playAudio(file) {
    return new Promise(resolve => {
        const audio = new Audio(file);
        audio.play();
        audio.onended = resolve;
    });
}

// Event listener for category filter selection
document.getElementById("categoryFilter").addEventListener("change", (event) => {
    filterAudioByCategory(event.target.value);
});
