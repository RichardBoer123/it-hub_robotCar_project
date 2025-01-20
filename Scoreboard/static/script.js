// Access the data passed from Flask
console.log("Data from Flask:", data);

// Get the container where the dynamic content will be added
const dataContainer = document.getElementById("data-container");

// Loop through the data array and create containers for each item
data.forEach(item => {
    // Create a container for each item with Bootstrap grid classes
    const col = document.createElement("div");
    col.classList.add("col-lg-4", "col-md-6", "col-sm-12", "mb-4"); // Responsive grid layout
    col.dataset.ip = item.ip;

    // Create a checkbox for selection
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.classList.add("data-checkbox"); // Add class to easily identify checkboxes

    // Create the inner container for each scoreboard item
    const container = document.createElement("div");
    container.classList.add("data-item", "border", "p-3"); // Add Bootstrap classes for border and padding

    // Add a border and background color to the container
    container.style.backgroundColor = "#f9f9f9"; // Light gray background

    // Create and append the <h1> element for IP address
    const h1 = document.createElement("h1");
    h1.textContent = item.ip;  // Use the "ip" field
    container.appendChild(h1);

    // Create and append the <p> element for timestamp
    const p = document.createElement("p");
    p.textContent = item.timestamp;  // Use the "timestamp" field
    container.appendChild(p);

    // Create and append the <iframe> element for camera feed
    const iframe = document.createElement("iframe");
    iframe.src = item.camera_feed;  // Use the "camera_feed" field
    iframe.width = "100%";
    iframe.height = "315";
    iframe.frameBorder = "0";
    iframe.allow = "autoplay; encrypted-media"; // Optional: allow autoplay for embedded media
    container.appendChild(iframe);

    // Append the checkbox to the column
    col.appendChild(checkbox);

    // Append the item container to the column
    col.appendChild(container);

    // Append the column to the data container (row)
    dataContainer.appendChild(col);
});

// Function to gather selected cars and trigger API calls
function startCar() {
    const selectedCars = [];
    const checkboxes = document.querySelectorAll('.data-checkbox');
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            const parentCol = checkbox.parentElement;
            const ip = parentCol.dataset.ip; // Assuming `ip` is the identifying field
            selectedCars.push(ip);
        }
    });

    if (selectedCars.length === 0) {
        alert("Please select at least one car!");
        return;
    }

    // Iterate through the selected cars and trigger API requests
    selectedCars.forEach(ip => {
        console.log("Sending request to:", ip);

        // Prepare the data for the POST request
        const payload = {
            action: "startMethod1"
        };

        // Send the POST request using fetch
        fetch(`http://${ip}/triggerAction/`, {
            method: 'POST',
            mode: 'no-cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();  // Parse JSON response
        })
        .then(data => {
            console.log(`Response from ${ip}:`, data);
            alert(`Action triggered successfully for ${ip}!`);
        })
        .catch(error => {
            console.error(`Error triggering action for ${ip}:`, error);
            alert(`Error triggering action for ${ip}.`);
        });
    });
}

// Add event listener for the button to trigger the API call
const triggerButton = document.getElementById("trigger-action-button");

triggerButton.addEventListener("click", startCar);
