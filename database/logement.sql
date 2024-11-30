-- Commandes pour détruire les tables
DROP TABLE IF EXISTS mesure;
DROP TABLE IF EXISTS facture;
DROP TABLE IF EXISTS capt_act;
DROP TABLE IF EXISTS type_capteur_actionneur;
DROP TABLE IF EXISTS piece;
DROP TABLE IF EXISTS logement;
DROP TABLE IF EXISTS users;  -- Ajout de la commande pour supprimer la table users si elle existe

-- Table des utilisateurs
CREATE TABLE users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,         -- ID unique de l'utilisateur
    name TEXT NOT NULL,                            -- Nom de l'utilisateur
    logement_id INTEGER NOT NULL,                  -- ID du logement, lié à la table logement
    password_hash TEXT NOT NULL,                   -- Mot de passe haché
    FOREIGN KEY (logement_id) REFERENCES logement(ID)  -- Référence à la table logement
);

-- Table des logements
CREATE TABLE logement (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,  -- Ajout du champ ID comme clé primaire
    IP TEXT,
    adress TEXT,
    num_tel TEXT,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des pièces d'un logement
CREATE TABLE piece (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location_x FLOAT,
    location_y FLOAT,
    location_z FLOAT,
    logement_id INTEGER,  -- Référence à l'ID du logement
    FOREIGN KEY (logement_id) REFERENCES logement (ID)  -- Correction de la clé étrangère
);

-- Table des types des capteurs/actionneurs
CREATE TABLE type_capteur_actionneur (
    name TEXT PRIMARY KEY,
    unite TEXT,
    precision TEXT
);

-- Table des capteurs/actionneurs dans une pièce
CREATE TABLE capt_act (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_commande TEXT,
    type TEXT,
    mesure FLOAT,
    port_com TEXT,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ref_piece INTEGER,
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
VALUES ('192.168.1.1', '123 Rue de l autmec', '0123456789');

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

-- Exemple d'insertion d'un utilisateur
-- On suppose que l'ID du logement est 1, et on crée un utilisateur avec un mot de passe haché.
INSERT INTO users (name, logement_id, password_hash)
VALUES 
('Jean Dupont', 1, 'hashed_password_here');  -- Utilise un mot de passe haché pour plus de sécurité
