// API Configuration
const API_KEY = '9037295e71930f4d1e7c96aebf6c807e';
const BASE_URL = 'https://api.openweathermap.org/data/2.5';

// DOM Elements
const cityInput = document.getElementById('city-input');
const searchBtn = document.getElementById('search-btn');
const locationElement = document.querySelector('.location');
const dateElement = document.querySelector('.date');
const tempElement = document.querySelector('.temp');
const iconElement = document.querySelector('.weather-icon');
const descriptionElement = document.querySelector('.description');
const windElement = document.querySelector('.detail-item:nth-child(1) div:last-child');
const humidityElement = document.querySelector('.detail-item:nth-child(2) div:last-child');
const pressureElement = document.querySelector('.detail-item:nth-child(3) div:last-child');
const forecastContainer = document.querySelector('.forecast-container');

// Utilities
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { weekday: 'short' });
}

function getWeatherIcon(iconCode) {
    const iconMap = {
        '01d': 'fa-sun', '01n': 'fa-moon',
        '02d': 'fa-cloud-sun', '02n': 'fa-cloud-moon',
        '03d': 'fa-cloud', '03n': 'fa-cloud',
        '04d': 'fa-cloud', '04n': 'fa-cloud',
        '09d': 'fa-cloud-showers-heavy', '09n': 'fa-cloud-showers-heavy',
        '10d': 'fa-cloud-sun-rain', '10n': 'fa-cloud-moon-rain',
        '11d': 'fa-bolt', '11n': 'fa-bolt',
        '13d': 'fa-snowflake', '13n': 'fa-snowflake',
        '50d': 'fa-smog', '50n': 'fa-smog'
    };
    return iconMap[iconCode] || 'fa-cloud';
}

// UI Functions
function setCurrentDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateElement.textContent = now.toLocaleDateString('en-US', options);
}

function showLoading() {
    forecastContainer.innerHTML = '<div class="loading"><div class="spinner"></div>Loading forecast...</div>';
}

function showError(message) {
    forecastContainer.innerHTML = `<div class="error-message">${message}</div>`;
}

function updateCurrentWeather(data) {
    const { name, sys, main, weather, wind } = data;
    locationElement.textContent = `${name}, ${sys.country}`;
    tempElement.textContent = `${Math.round(main.temp)}°C`;
    descriptionElement.textContent = weather[0].description;
    iconElement.innerHTML = `<i class="fas ${getWeatherIcon(weather[0].icon)}"></i>`;
    windElement.textContent = `${wind.speed} m/s`;
    humidityElement.textContent = `${main.humidity}%`;
    pressureElement.textContent = `${main.pressure} hPa`;
}

function updateForecast(forecastData) {
    forecastContainer.innerHTML = '';
    const dailyForecasts = {};

    forecastData.list.forEach(item => {
        const date = item.dt_txt.split(" ")[0];
        if (!dailyForecasts[date]) {
            dailyForecasts[date] = {
                date: item.dt_txt,
                temp_min: item.main.temp_min,
                temp_max: item.main.temp_max,
                icon: item.weather[0].icon
            };
        } else {
            dailyForecasts[date].temp_min = Math.min(dailyForecasts[date].temp_min, item.main.temp_min);
            dailyForecasts[date].temp_max = Math.max(dailyForecasts[date].temp_max, item.main.temp_max);
        }
    });

    Object.values(dailyForecasts).slice(0, 5).forEach(forecast => {
        const forecastItem = document.createElement('div');
        forecastItem.className = 'forecast-item';
        forecastItem.innerHTML = `
            <div class="forecast-date">${formatDate(forecast.date)}</div>
            <div class="forecast-icon"><i class="fas ${getWeatherIcon(forecast.icon)}"></i></div>
            <div class="forecast-temp">${Math.round(forecast.temp_max)}° / ${Math.round(forecast.temp_min)}°</div>
        `;
        forecastContainer.appendChild(forecastItem);
    });
}

// API Functions
async function fetchWeatherByCity(city) {
    const response = await fetch(`${BASE_URL}/weather?q=${city}&appid=${API_KEY}&units=metric`);
    if (!response.ok) throw new Error('City not found');
    return response.json();
}

async function fetchForecastByCity(city) {
    const response = await fetch(`${BASE_URL}/forecast?q=${city}&appid=${API_KEY}&units=metric`);
    if (!response.ok) throw new Error('Forecast data unavailable');
    return response.json();
}

async function fetchWeatherByCoords(lat, lon) {
    const response = await fetch(`${BASE_URL}/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`);
    if (!response.ok) throw new Error('Weather data unavailable');
    return response.json();
}

async function fetchForecastByCoords(lat, lon) {
    const response = await fetch(`${BASE_URL}/forecast?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`);
    if (!response.ok) throw new Error('Forecast data unavailable');
    return response.json();
}

// Controllers
async function getWeather(city) {
    showLoading();
    try {
        const data = await fetchWeatherByCity(city);
        updateCurrentWeather(data);

        const forecastData = await fetchForecastByCity(city);
        updateForecast(forecastData);
    } catch (error) {
        showError(`Error: ${error.message}`);
        console.error(error);
    }
}

async function getWeatherByLocation(lat, lon) {
    showLoading();
    try {
        const data = await fetchWeatherByCoords(lat, lon);
        updateCurrentWeather(data);

        const forecastData = await fetchForecastByCoords(lat, lon);
        updateForecast(forecastData);
    } catch (error) {
        showError(`Error: ${error.message}`);
        console.error(error);
    }
}

// Event Listeners
searchBtn.addEventListener('click', () => {
    if (cityInput.value.trim()) getWeather(cityInput.value.trim());
});

cityInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter' && cityInput.value.trim()) getWeather(cityInput.value.trim());
});

window.addEventListener('load', () => {
    setCurrentDate();
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                getWeatherByLocation(latitude, longitude);
            },
            () => {
                // Fallback if user denies location access
                getWeather('Mumbai');
            }
        );
    } else {
        // Fallback if geolocation not supported
        getWeather('Mumbai');
    }
});