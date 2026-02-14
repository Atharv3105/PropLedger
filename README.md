# 🌤️ Weather Dashboard

A robust, responsive weather application built with vanilla JavaScript that provides real-time weather data and a 5-day forecast for cities worldwide. It features automatic geolocation, error handling, and a clean user interface.

![Weather App Preview](https://via.placeholder.com/800x400?text=App+Screenshot+Here) 
*(Tip: Replace the link above with a screenshot of your actual app)*

## ✨ Features

* **📍 Automatic Geolocation:** Detects user location on load to display local weather.
* **🔍 City Search:** Search for weather conditions in any city globally.
* **🌡️ Real-Time Data:** Displays temperature, humidity, wind speed, and pressure.
* **📅 5-Day Forecast:** Shows daily high/low temperatures and weather conditions.
* **🎨 Dynamic UI:** Updates icons and visuals based on weather conditions (e.g., rain, clouds, clear sky).
* **🔒 Secure Configuration:** API keys are managed separately for security.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **API:** [OpenWeatherMap API](https://openweathermap.org/api)
* **Icons:** [FontAwesome](https://fontawesome.com/)

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

1.  **Git** installed on your machine.
2.  An **API Key** from OpenWeatherMap (Free tier works fine).

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/your-username/weather-app.git](https://github.com/your-username/weather-app.git)
    cd weather-app
    ```

2.  **Create the Configuration File**
    Since the API key is secured and not uploaded to GitHub, you must create a `config.js` file manually.
    
    * Create a file named `config.js` in the root folder.
    * Add the following code, replacing `'YOUR_API_KEY'` with your actual key:
    
    ```javascript
    // config.js
    const CONFIG = {
        API_KEY: 'YOUR_OPENWEATHERMAP_API_KEY_HERE'
    };
    ```

3.  **Run the App**
    Simply open `index.html` in your web browser.

## 📂 Project Structure

```text
weather-app/
├── index.html      # Main HTML structure
├── style.css       # Responsive styling
├── script.js       # Main application logic
├── config.js       # API Key configuration (Not in repo)
└── README.md       # Project documentation
