function clearAll() {
  // Use SweetAlert2 for confirmation popup
  Swal.fire({
      title: 'Verwijderen data?',
      text: "Weet je zeker dat je alle robotauto data wilt verwijderen?",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Ja, verwijder!',
      cancelButtonText: 'Annuleer'
  }).then((result) => {
      if (result.isConfirmed) {
          // Clear the card-container innerHTML
          const parentContainer = document.getElementById("card-container");
          if (parentContainer) {
              parentContainer.innerHTML = ""; // Remove all child elements
              console.log("Card container cleared.");
          }

          // Call the server to clear the data.json file
          fetch('/clear-data', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
          })
          .then((response) => {
              if (response.ok) {
                  return response.json();
              } else {
                  throw new Error('Failed to clear data.json');
              }
          })
          .then((data) => {
              Swal.fire(
                  'Verwijderd!',
                  'Alle data is verwijderd.',
                  'success'
              );
          })
          .catch((error) => {
              console.error('Error:', error);
              Swal.fire(
                  'Oeps!',
                  'Er is iets misgegaan tijdens het verwijderen!',
                  'error'
              );
          });
      }
  });
}

async function checkCameraFeed(httpAddress, key) {
  try {
    const response = await fetch(httpAddress, { method: "HEAD" });
    if (response.ok) {
      console.log(`Camera feed at "${httpAddress}" is reachable.`);
      return true; // Feed is valid
    } else {
      throw new Error(`Camera feed unreachable: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error(`Error checking camera feed at "${httpAddress}":`, error);

    // Send a DELETE request to remove the device with this IP
    try {
      const deleteResponse = await fetch('/delete-key', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ key }), // Pass the IP as the key
      });

      if (deleteResponse.ok) {
        console.log(`Key (IP) "${key}" successfully deleted.`);
      } else {
        const deleteError = await deleteResponse.json();
        console.error(`Failed to delete key (IP) "${key}":`, deleteError.error);
      }
    } catch (deleteError) {
      console.error(`Error deleting key (IP) "${key}":`, deleteError);
    }

    return false; // Feed is invalid
  }
}


// Function to start the countdown
function startCounter(deviceIp) {
  const counterElement = document.getElementById(`counter-${deviceIp}`);

  let seconds = 0;
  const interval = setInterval(() => {
      const minutes = Math.floor(seconds / 60);
      const displaySeconds = seconds % 60;
      
      // Format time as MM:SS
      const timeString = `${minutes.toString().padStart(2, '0')}:${displaySeconds.toString().padStart(2, '0')}`;
      
      counterElement.textContent = timeString;

      seconds += 1;

      // Assuming iframe loads successfully, you can clear the interval
      const iframe = counterElement.closest(".card").querySelector("iframe");
      if (iframe && iframe.complete) {
          clearInterval(interval); // Stop the counter when iframe finishes loading
      }

  }, 1000); // Increment every second
}

// Call `startCounter` for each device's IP after getting data
function createCard(device, index) {
   // Determine display name
   const displayName = device.custom_name || device.ip;

   // Determine card title label
   const cardLabel = device.last_drive_time ? `${index + 1}#` : "Nog niet gereden";
 
   // Best time display
   const bestTimeDisplay = device.best_time ? `Best Time: ${device.best_time}` : "Best Time: N/A";

  
  const cardContent = `
    <div class="card-body">
      <div class="form-check">
        <input class="form-check-input" type="checkbox" value="" id="select-${device.ip}">
        <label class="form-check-label" for="select-${device.ip}">
          Select
        </label>
      </div>
      <h5 class="card-title">${cardLabel}</h5>
      <p class="card-text" id="card-text-${index}">
        ${displayName}
        <button class="btn mx-1 edit-btn" onclick="editCardName(${index}, '${device.ip}', '${displayName}')">
          <i class="bi bi-pencil-square"></i>
        </button>
      </p>
      <p class="card-text counter" id="counter-${device.ip}">00:00</p>
      <p class="card-text best-time">${bestTimeDisplay}</p> <!-- Best Time Placeholder -->
      <button onclick="stopCar('${device.ip}')">Stop car</button>
    </div>
    <iframe id="iframe${index + 1}" class="card-img-top" src="${device.camera_feed}" frameborder="0"></iframe>
  `;

  const card = document.createElement("div");
  card.className = "card robotCar";
  card.setAttribute("data-ip", device.ip);
  card.style.width = "18rem";
  card.innerHTML = cardContent;

  return card;
}

function syncData() { 
  fetch("/get-data")
    .then((res) => res.json()) // Parse the response as JSON
    .then((data) => {
      if (Array.isArray(data)) {
        const parentContainer = document.getElementById("card-container");
        const existingCards = Array.from(parentContainer.getElementsByClassName("card"));

        // Find card IPs from existing cards
        const existingCardIPs = existingCards.map(card => card.getAttribute('data-ip'));

        // Filter the new data to only get devices not present in existing cards
        const newData = data.filter(device => !existingCardIPs.includes(device.ip));

        // Append new cards
        newData.forEach((device, index) => {
          const card = createCard(device, index);
          parentContainer.appendChild(card);
        });

        // Remove outdated cards
        existingCards.forEach(card => {
          const cardIP = card.getAttribute('data-ip');
          if (!data.some(device => device.ip === cardIP)) {
            card.remove();
          }
        });
      } else {
        console.error("Data is not an array.");
      }
    })
    .catch((e) => console.error("Error:", e));
}

async function getData() {
  try {
    const response = await fetch("/get-data");
    const data = await response.json();

    if (Array.isArray(data)) {
      const parentContainer = document.getElementById("card-container");
      parentContainer.innerHTML = ""; // Clear existing content

      for (const [index, device] of data.entries()) {
        const isFeedValid = true; //await checkCameraFeed(device.camera_feed, device.ip);
        if (isFeedValid) {
          const card = createCard(device, index);
          parentContainer.appendChild(card);
        } else {
          console.warn(`Camera feed for device ${device.ip} is invalid. Skipping card creation.`);
        }
      }
    } else {
      console.error("Data is not an array.");
    }
  } catch (e) {
    console.error("Error fetching data:", e);
  }
}

function editCardName(index, deviceIp, currentName) {
  Swal.fire({
    title: 'Verander de naam van de robotauto!',
    html: `
      <form id="edit-name-form">
        <label for="newName" style="display: block; margin-bottom: 8px;">Nieuwe naam:</label>
        <input type="text" id="newName" class="swal2-input" value="${currentName}" required>
      </form>
    `,
    showCancelButton: true,
    confirmButtonText: 'Opslaan',
    cancelButtonText: 'Annuleer',
    preConfirm: () => {
      const newName = document.getElementById('newName').value.trim();
      if (!newName) {
        Swal.showValidationMessage('Verander hier de naam in!');
      }
      return newName;
    },
  }).then((result) => {
    if (result.isConfirmed) {
      const updatedName = result.value;

      // Make a PUT request to update the custom name in the backend
      fetch('/update-custom-name', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ip: deviceIp,
          custom_name: updatedName,
        }),
      })
        .then((response) => {
          if (response.ok) {
            // Update the name in the DOM if successful
            const cardTextElement = document.getElementById(`card-text-${index}`);
            if (cardTextElement) {
              cardTextElement.childNodes[0].textContent = updatedName; // Update only the name, not the button
            }
            Swal.fire('Success', 'De naam is succesvol aangepast!', 'success');
          } else {
            response.json().then((data) => {
              Swal.fire('Error', data.error || 'Er is iets foutgegaan met het aanpassen van de naam!', 'error');
            });
          }
        })
        .catch((error) => {
          Swal.fire('Error', 'Failed to communicate with the server', 'error');
          console.error('Error:', error);
        });
    }
  });
}

// Function to start selected robots
function startSelectedCars() {
  const selectedCards = document.querySelectorAll(".robotCar input.form-check-input:checked");

  selectedCards.forEach(card => {
    const ip = card.closest('.robotCar').getAttribute('data-ip');
    card.closest('.robotCar').style.border = "2px solid green"; // Apply green border
    
    // Start the counter for each card
    const counterElement = document.getElementById(`counter-${ip}`);
    if (counterElement) {
      clearInterval(counterElement._interval);
      let seconds = 0;
      const interval = setInterval(() => {
        const minutes = Math.floor(seconds / 60);
        const displaySeconds = seconds % 60;
        
        // Format time as MM:SS
        const timeString = `${minutes.toString().padStart(2, '0')}:${displaySeconds.toString().padStart(2, '0')}`;
        
        counterElement.textContent = timeString;

        seconds += 1;

        // Assuming iframe loads successfully, you can clear the interval
        const iframe = card.closest('.robotCar').querySelector("iframe");
        if (iframe && iframe.complete) {
          clearInterval(interval); // Stop the counter when iframe finishes loading
        }

      }, 1000); // Increment every second

      // Store the interval in a custom property for stopping individually
      counterElement._interval = interval;
    }
  });
}

// Function to start all car counters
function startAllCars() {
  const greenCards = document.querySelectorAll(".robotCar");
  
  greenCards.forEach(card => {
    card.style.border = "2px solid green"; // Apply green border
    
    // Start the counter for each card
    const counterElement = card.querySelector(".counter");
    if (counterElement) {
      clearInterval(counterElement._interval);
      let seconds = 0;
      const interval = setInterval(() => {
        const minutes = Math.floor(seconds / 60);
        const displaySeconds = seconds % 60;
        
        // Format time as MM:SS
        const timeString = `${minutes.toString().padStart(2, '0')}:${displaySeconds.toString().padStart(2, '0')}`;
        
        counterElement.textContent = timeString;

        seconds += 1;

        // Assuming iframe loads successfully, you can clear the interval
        const iframe = card.querySelector("iframe");
        if (iframe && iframe.complete) {
          clearInterval(interval); // Stop the counter when iframe finishes loading
        }

      }, 1000); // Increment every second

      // Store the interval in a custom property for stopping individually
      counterElement._interval = interval;
    }
  });
}

// Function to stop an individual car counter
function stopCar(ip) {
  const card = document.querySelector(`.robotCar[data-ip="${ip}"]`);
  if (card) {
    const counterElement = document.getElementById(`counter-${ip}`);
    console.log(counterElement);
    if (counterElement) {
      clearInterval(counterElement._interval); // Clear the specific interval
    }
    card.style.border = ""; // Remove green border
  }
  setTimeout(function() {
    sortCardsByTime();
  },1000);
}

function sortCardsByTime() {
  // Select all robotCar cards
  const cards = document.querySelectorAll(".robotCar");

  // Convert NodeList to array for sorting
  const cardArray = Array.from(cards);

  // Sort cards based on the counter value and maintain relative order for ties
  cardArray.sort((a, b) => {
    const positionA = parseInt(a.querySelector(".card-title").textContent.replace('#', '').trim());
    const positionB = parseInt(b.querySelector(".card-title").textContent.replace('#', '').trim());

    const timeA = a.querySelector(".counter").textContent;
    const timeB = b.querySelector(".counter").textContent;

    // Convert times to seconds for comparison
    const [minutesA, secondsA] = timeA.split(":").map(Number);
    const [minutesB, secondsB] = timeB.split(":").map(Number);

    // Calculate total seconds for sorting
    const totalSecondsA = minutesA * 60 + secondsA;
    const totalSecondsB = minutesB * 60 + secondsB;

    if (totalSecondsA === totalSecondsB) {
      // If times are the same, maintain their current relative order based on original position
      return positionA - positionB;
    }

    return totalSecondsA - totalSecondsB; // Ascending order (lowest time first)
  });

  // Update the card titles to reflect their new positions
  cardArray.forEach((card, index) => {
    const cardTitle = card.querySelector(".card-title");
    cardTitle.textContent = `${index + 1}#`; // Update position
  });

  // Append sorted cards to the parent container
  const parentContainer = document.getElementById("card-container");
  parentContainer.innerHTML = ""; // Clear existing content
  cardArray.forEach(card => parentContainer.appendChild(card));

}