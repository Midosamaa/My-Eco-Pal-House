#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 14        // Pin pour le DHT11 (ici D2)
#define DHTTYPE DHT11    // Définir le type de capteur (DHT11)

#define LED_PIN 2        // Pin GPIO pour la LED (ici D4)

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "iPhone de Aymane";        // Ton SSID Wi-Fi
const char* password = "12345678"; // Ton mot de passe Wi-Fi
const char* mqtt_server = "172.20.10.2"; // Adresse de ton broker MQTT

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  delay(10);
  dht.begin();

  pinMode(LED_PIN, OUTPUT);  // Configurer la LED comme une sortie

  // Connexion au réseau Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connexion au WiFi...");
  }
  Serial.println("Connecté au WiFi");

  client.setServer(mqtt_server, 1883); // Connexion au broker MQTT
  client.setCallback(mqttCallback);    // Callback pour recevoir des messages MQTT
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentative de connexion MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println("Connecté");
      client.subscribe("maison/led");  // S'abonner au topic "maison/led" pour recevoir les commandes
    } else {
      Serial.print("Échec, code de retour : ");
      Serial.print(client.state());
      delay(1000);
    }
  }
}

// Callback appelé lorsqu'un message est reçu sur un topic
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  // Si le message est "ON", allumer la LED
  if (message == "ON") {
    digitalWrite(LED_PIN, LOW);
    Serial.println("LED allumée");
  }
  // Si le message est "OFF", éteindre la LED
  else if (message == "OFF") {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("LED éteinte");
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  delay(1000);  // Attendre 3 secondes entre les lectures

  // Lire la température et l'humidité
  float temp = dht.readTemperature(); // Température en Celsius
  float humid = dht.readHumidity();   // Humidité en pourcentage

  if (isnan(temp) || isnan(humid)) {
    Serial.println("Échec de la lecture du capteur DHT!");
    return;
  }

  // Afficher dans le moniteur série
  Serial.print("Température: ");
  Serial.print(temp);
  Serial.print("°C");
  Serial.print(" Humidité: ");
  Serial.print(humid);
  Serial.println("%");

  // Créer le message JSON avec les données de température et d'humidité
  String payload = String("{\"temperature\":") + temp + ", \"humidity\":" + humid + "}";

  // Publier les données sur le topic "maison/capteurs/dht11"
  client.publish("maison/capteurs/dht11", payload.c_str());

  delay(1000); // Envoi toutes les 3 secondes
}
