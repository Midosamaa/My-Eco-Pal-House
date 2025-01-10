-- Commandes pour détruire les tables
DROP TABLE IF EXISTS mesure;
DROP TABLE IF EXISTS facture;
DROP TABLE IF EXISTS capt_act;
-- DROP TABLE IF EXISTS type_capteur_actionneur;
DROP TABLE IF EXISTS piece;
DROP TABLE IF EXISTS logement;
-- DROP TABLE IF EXISTS users;  -- Ajout de la commande pour supprimer la table users si elle existe

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    logement_id INTEGER,
    email TEXT UNIQUE,  -- Contraintes d'unicité
    password_hash TEXT NOT NULL,
    FOREIGN KEY (logement_id) REFERENCES logement (id)
);

-- Table des logements
CREATE TABLE IF NOT EXISTS logement (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,  -- Ajout du champ ID comme clé primaire
    IP TEXT,
    adress TEXT,
    num_tel TEXT,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des pièces d'un logement
CREATE TABLE IF NOT EXISTS piece (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location_x FLOAT,
    location_y FLOAT,
    location_z FLOAT,
    logement_id INTEGER,  -- Référence à l'ID du logement
    FOREIGN KEY (logement_id) REFERENCES logement (ID)  -- Correction de la clé étrangère
);

-- Table des types des capteurs/actionneurs
CREATE TABLE IF NOT EXISTS type_capteur_actionneur (
    name TEXT PRIMARY KEY,
    unite TEXT,
    precision TEXT
);

-- Modified Table for Sensors/Actuators
CREATE TABLE IF NOT EXISTS capt_act (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_commande TEXT,
    type TEXT,
    mesure FLOAT,
    port_com TEXT,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ref_piece INTEGER,
    etat TEXT DEFAULT 'off',  -- New field for the status (on/off)
    FOREIGN KEY (ref_piece) REFERENCES piece (ID),
    FOREIGN KEY (type) REFERENCES type_capteur_actionneur (name)
);


-- Table des relevés des mesures des capteurs
CREATE TABLE mesure (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_capt_act INTEGER,
    value FLOAT,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_capt_act) REFERENCES capt_act (ID)
);

-- Table des factures d'un logement
CREATE TABLE facture (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    date_fact DATE,
    montant FLOAT,
    val_consommee FLOAT,
    logement_id INTEGER,  -- Référence à l'ID du logement
    FOREIGN KEY (logement_id) REFERENCES logement (ID)
);

-- Insertion d'un logement
INSERT INTO logement (IP, adress, num_tel) 
VALUES 
('192.168.1.1', '123 Rue de l autmec', '0123456789'),
('169.169.6.9', '69 Rue de l autmec', '0123456789');

-- Récupérer l'ID du logement récemment inséré
SELECT last_insert_rowid();

-- Insertion des pièces associées au logement (en utilisant l'ID du logement)
-- Remarque : ici, on suppose que l'ID du logement inséré est 1
-- Il est préférable de récupérer dynamiquement l'ID du logement via une requête SELECT en Python.
INSERT INTO piece (name, location_x, location_y, location_z, logement_id) 
VALUES 
('Salon', 0.0, 0.0, 0.0, 1),   -- L'ID du logement est 1
('Cuisine', 5.0, 0.0, 0.0, 1),
('Chambre 1', 0.0, 5.0, 3.0, 1),
('Salle de bain', 5.0, 5.0, 3.0, 1);

-- Insertion de 4 types de capteurs/actionneurs dans la table type_capteur_actionneur
INSERT INTO type_capteur_actionneur (name, unite, precision) 
VALUES 
('Capteur de température', '°C', '0.1'),
('Capteur de luminosité', 'lux', '1'),
('Capteur d humidité', '%', '0.5'),
('Actionneur de volet', 'N/A', 'N/A');

-- Insertion de capteurs/actionneurs dans la table capt_act
-- Associer ces capteurs aux pièces par leurs IDs respectifs
INSERT INTO capt_act (ref_commande, type, mesure, port_com, ref_piece)
VALUES 
('CMD_TEMP_001', 'Capteur de température', 22.5, 'PORT_1', 1),  -- Associer à la pièce avec ID 1
('CMD_LUM_002', 'Capteur de luminosité', 350, 'PORT_2', 2);     -- Associer à la pièce avec ID 2

-- Insertion de 2 mesures pour le capteur/actionneur avec l'ID 1 (Capteur de température)
INSERT INTO mesure (ID_capt_act, value)
VALUES 
(1, 22.5),  -- Première mesure
(1, 23.0);  -- Deuxième mesure

-- Insertion de 2 mesures pour le capteur/actionneur avec l'ID 2 (Capteur de luminosité)
INSERT INTO mesure (ID_capt_act, value)
VALUES 
(2, 350),   -- Première mesure
(2, 355);   -- Deuxième mesure

-- Insertion de 4 factures dans la table facture
-- Utilisation de l'ID du logement (1) dans les factures
INSERT INTO facture (type, date_fact, montant, val_consommee, logement_id)
VALUES 
('Électricité', '2024-01-15', 120.50, 300.0, 1),  -- Facture 1 associée au logement avec ID 1
('Eau', '2024-02-10', 45.75, 50.0, 1),            -- Facture 2 associée au même logement
('Gaz', '2024-03-20', 89.30, 150.0, 1),           -- Facture 3
('Internet', '2024-04-05', 60.00, 1.0, 1);        -- Facture 4

-- Insertion de nouvelles pièces dans la maison avec l'ID 2
INSERT INTO piece (name, location_x, location_y, location_z, logement_id) 
VALUES 
('Bureau', 20.0, 0.0, 0.0, 2),    -- Bureau dans la maison avec ID 2
('Chambre 2', 0.0, 0.0, 20.0, 2),  -- Chambre 2 dans la maison avec ID 2
('Salle à manger', 20.0, 0.0, 20.0, 2), -- Salle à manger dans la maison avec ID 2
('Garage', 0.0, 0.0, 0.0, 2);    -- Garage dans la maison avec ID 2

-- Insertion de nouvelles pièces dans la maison avec l'ID 3
INSERT INTO piece (name, location_x, location_y, location_z, logement_id) 
VALUES 
('Bureau', 10.0, 0.0, 0.0, 3),    -- Bureau dans la maison avec ID 2
('Chambre 2', 0.0, 20.0, 10.0, 3),  -- Chambre 2 dans la maison avec ID 2
('Salle à manger', 5.0, -5.0, 0.0, 3), -- Salle à manger dans la maison avec ID 2
('Garage', 20.0, 20.0, -5.0, 3);    -- Garage dans la maison avec ID 2

-- Insertion de capteurs/actionneurs pour ces nouvelles pièces
INSERT INTO capt_act (ref_commande, type, mesure, port_com, ref_piece, etat)
VALUES 
-- Bureau
('CMD_TEMP_003', 'Capteur de température', 21.5, 'PORT_3', 5, 'on'),  -- Temperature sensor in Bureau (room 5)
-- Chambre 2
('CMD_MOTION_001', 'Capteur de mouvement', 0, 'PORT_4', 6, 'on'),    -- Motion sensor in Chambre 2 (room 6)
-- Salle à manger
('CMD_HUM_001', 'Capteur d humidité', 45.0, 'PORT_5', 7, 'off'),     -- Humidity sensor in Salle à manger (room 7)
-- Garage
('CMD_VOLET_001', 'Actionneur de volet', 1, 'PORT_6', 8, 'on');      -- Actuator for garage shutter in Garage (room 8)

INSERT INTO capt_act (ref_commande, type, mesure, port_com, ref_piece, etat)
VALUES 
-- Bureau
('CMD_TEMP_004', 'Capteur de température', 21.5, 'PORT_3', 9, 'off'),  -- Temperature sensor in Bureau (room 5)
-- Chambre 2
('CMD_MOTION_012', 'Capteur de mvt', 0, 'PORT_4', 10, 'off'),    -- Motion sensor in Chambre 2 (room 6)
-- Salle à manger
('CMD_HUM_101', 'Capteur d hum', 45.0, 'PORT_5', 11, 'off'),     -- Humidity sensor in Salle à manger (room 7)
-- Garage
('CMD_VOLET_505', 'Actionneur de lumiere', 1, 'PORT_6', 12, 'off');      -- Actuator for garage shutter in Garage (room 8)
