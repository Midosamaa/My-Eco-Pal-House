Eco-Friendly Housing Management System
This project is designed to help homeowners manage and optimize energy consumption in an eco-friendly housing environment. The system allows users to track the consumption of electricity, water, gas, and internet while providing functionalities for device control, consumption tracking, savings insights, and more.

Prerequisites
To run this project, ensure you have the following software installed:

Arduino IDE: Required for uploading and interacting with the DHT11 sensor.
Python 3: The backend of the system is built using Python 3.
SQLite 3: Used for database management.
Additionally, make sure all necessary Python libraries are up to date. The libraries used are listed in the Python files.

You will also need the DHT11 library for Arduino. You can find and install it via the Arduino IDE.

Project Directory Structure
Your working directory should look like this:

arduino

.
├── back
│   ├── fill.py
│   ├── led.py
│   ├── logement.db
│   └── README.md
├── database
│   ├── logement.db
│   └── logement.sql
├── dht11
│   └── dht11.ino
├── front
│   └── html
│       ├── capteurs.html
│       ├── change-password.html
│       ├── configuration.html
│       ├── consommation.html
│       ├── economies.html
│       ├── home.html
│       ├── inscription.html
│       ├── login.html
│       └── mesure.html
└── static
    ├── css
    │   └── styles.css
    ├── images
    │   └── account-icon2.png
    └── js
        └── scripts.js
Installation
Follow these steps to get the project running locally:

1. Clone the Repository
First, clone the repository to your local machine:


git clone https://github.com/Midosamaa/My-Eco-Pal-House
cd eco-friendly-housing

2. Set up the Database
Go to the database folder and run the following command to create the necessary SQLite database:

sqlite3 logement.db < logement.sql


3. Configure MQTT Broker
Open the led.py file in the back folder and navigate to line 298. Change the MQTT broker address to the correct one. To find the address, run the command:

ifconfig

Copy the IP address from the output and paste it into the led.py file.

4. Configure Arduino (DHT11 Sensor)
Open the dht11.ino file located in the dht11 folder. Modify the following lines with your own Wi-Fi credentials:


char ssid[] = "your_network_name"; // Replace with your network name
char pass[] = "your_network_password"; // Replace with your network password
Additionally, modify the mqtt_server variable with the IP address you copied earlier.
Upload the file on the ESP8266 with the DHT11 plugged on the pin 14.

5. Run the Backend Server
In the back folder, run the following command to start the backend server:

python3 led.py
This will run the server on localhost. You can then Ctrl + Left-click the address shown in the terminal to access the web interface.

Usage
Once the server is running, navigate to http://localhost:5000 (or whichever address is displayed) in your browser.

Account Management
Sign In: If you already have an account, go ahead and sign in.
Sign Up: If you don’t have an account, click on "Créer un compte" to sign up. You will be directed to a registration form where you need to fill in your information. After submitting the form, your account will be added to the database.

After signing in, you will be redirected to the Home Page, where you will find an overview of your house, including energy consumption, device management, and savings insights.

At the top of the page, you'll find a navigation panel. Here’s a brief description of each section:

1. Accueil (Home)
Clicking on Accueil will bring you back to the Home Page, where you can access a summary of all key data related to your home.

2. Consommation (Consumption)
By clicking on Consommation, you will be redirected to the Consumption Page. Here, you’ll find:

A pie chart showing the breakdown of your energy consumption.
A section with helpful tips on how to reduce your consumption.
To explore more detailed information for a specific type of consumption, click on the corresponding section of the pie chart. This will display:

A line graph showing trends over time.
A table providing detailed consumption data for that category.

3. Capteurs/Actionneurs (Sensors/Actuators)
Clicking on Capteurs/Actionneurs takes you to a page where you’ll find all the sensors and actuators installed in your house. The page includes:

A 3D model of your home’s layout, showing the locations of rooms and sensors.
A toggle switch to activate or deactivate sensors and actuators, giving you control over your devices directly from the interface.

4. Mesures (Measures)
Clicking on Mesures will bring you to a page displaying the data collected by the DHT11 sensors. Here, you’ll find:

A table listing the temperature and humidity readings.
Graphs visualizing the temperature and humidity data trends over time.

5. Économies (Savings)
By clicking on Économies, you will be redirected to the Savings Page. On this page, you’ll find:

Tips on how to change your practices to save more energy.
Buttons for each type of consumption/bill. Clicking any of these buttons will display detailed data on the savings you’ve made over the months, including:
A comparison of your monthly consumption versus the average consumption for each bill type.
A table with numerical values showing your energy-saving progress.

6. Configuration (Configuration)
Clicking on Configuration will take you to the Configuration Page, where you can:

Add new bills (factures).
View a list of sensors and actuators.
Add new sensors and actuators to the system.

By clicking on the house icon in the top right corner, you can choose to either change your password or log out.

Se Deconnecter: Clicking this option will log you out and redirect you to the login page.
Changer de mot de passe: Clicking on Change Password will take you to the change password page, where you’ll be prompted to fill in the necessary form. However, please note that this functionality is currently not implemented, so we recommend choosing your password wisely for now! 😄