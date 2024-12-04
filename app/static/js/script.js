// Socket.IO connection
const socket = io.connect(location.origin);

// DOM Elements
const cameraStream = document.getElementById("camera-stream");
const onlineStream = document.getElementById("online-stream");
const processedCanvas = document.getElementById("processed-canvas");
const alertMessage = document.getElementById("alert-message");
const startCameraBtn = document.getElementById("start-camera");
const stopCameraBtn = document.getElementById("stop-camera");
const startStreamBtn = document.getElementById("start-stream");
const stopStreamBtn = document.getElementById("stop-stream");
const streamUrlInput = document.getElementById("stream-url");

// Canvas Context
const ctx = processedCanvas.getContext("2d");

// Global Variables
let localStream = null;
let onlineStreamInterval = null;
let backendProcessingInterval = null;

/* =============================== */
/* Local Camera Stream Management */
/* =============================== */
startCameraBtn.addEventListener("click", async () => {
    try {
        // Get video stream from the user's camera
        localStream = await navigator.mediaDevices.getUserMedia({ video: true });
        cameraStream.srcObject = localStream;
        startCameraBtn.disabled = true;
        stopCameraBtn.disabled = false;

        // Start sending frames to backend for processing
        backendProcessingInterval = setInterval(() => {
            sendFrameToBackend(cameraStream);
        }, 1000); // Send every 1 second
    } catch (err) {
        console.error("Error accessing camera:", err);
        alert("Error accessing camera: " + err.message);
    }
});

stopCameraBtn.addEventListener("click", () => {
    // Stop the local camera stream
    if (localStream) {
        const tracks = localStream.getTracks();
        tracks.forEach((track) => track.stop());
        cameraStream.srcObject = null;
    }
    clearInterval(backendProcessingInterval);
    startCameraBtn.disabled = false;
    stopCameraBtn.disabled = true;
});

/* ================================ */
/* Online Video Stream Management  */
/* ================================ */
startStreamBtn.addEventListener("click", () => {
    const streamUrl = streamUrlInput.value;

    if (!streamUrl) {
        alert("Please enter a valid stream URL.");
        return;
    }

    // Use <video> element to stream the online video
    onlineStream.src = streamUrl;
    onlineStream.crossOrigin = "anonymous"; // Allow cross-origin for processing
    onlineStream.play();

    // Start sending frames to backend for processing
    stopStreamBtn.disabled = false;
    startStreamBtn.disabled = true;

    onlineStreamInterval = setInterval(() => {
        sendFrameToBackend(onlineStream);
    }, 1000); // Send every 1 second
});

stopStreamBtn.addEventListener("click", () => {
    // Stop the online stream
    onlineStream.src = "";
    clearInterval(onlineStreamInterval);
    stopStreamBtn.disabled = true;
    startStreamBtn.disabled = false;
});

/* ========================= */
/* Send Frames to the Backend */
/* ========================= */
function sendFrameToBackend(videoElement) {
    if (!videoElement.srcObject && !videoElement.src) {
        console.warn("No video source available.");
        return;
    }

    // Draw the current video frame on the canvas
    processedCanvas.width = videoElement.videoWidth;
    processedCanvas.height = videoElement.videoHeight;
    ctx.drawImage(videoElement, 0, 0, processedCanvas.width, processedCanvas.height);

    // Convert canvas data to a blob (image)
    processedCanvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append("frame", blob, "frame.jpg");

        // Send the frame to the backend
        fetch("/process-frame", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                // Render processed results on canvas
                updateCanvas(data);
            })
            .catch((err) => {
                console.error("Error sending frame to backend:", err);
            });
    }, "image/jpeg");
}

/* ========================= */
/* Update Canvas with Results */
/* ========================= */
function updateCanvas(data) {
    if (data.bounding_boxes && data.labels) {
        // Draw bounding boxes and labels
        ctx.clearRect(0, 0, processedCanvas.width, processedCanvas.height); // Clear canvas
        ctx.drawImage(cameraStream, 0, 0, processedCanvas.width, processedCanvas.height); // Redraw original frame

        data.bounding_boxes.forEach((box, index) => {
            const [x, y, width, height] = box;
            const label = data.labels[index];

            // Draw the bounding box
            ctx.strokeStyle = "red";
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, width, height);

            // Draw the label
            ctx.fillStyle = "red";
            ctx.font = "16px Arial";
            ctx.fillText(label, x, y - 5);
        });
    }
}

/* ======================= */
/* Real-Time Alert Updates */
/* ======================= */
socket.on("new_alert", (data) => {
    alertMessage.textContent = data.message;
    alertMessage.style.display = "block";

    setTimeout(() => {
        alertMessage.style.display = "none";
    }, 5000); // Hide after 5 seconds
});