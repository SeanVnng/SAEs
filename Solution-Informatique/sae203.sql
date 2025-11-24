CREATE TABLE site (
    idsite SERIAL PRIMARY KEY,
    nomsite VARCHAR(100) NOT NULL
);

CREATE TABLE client (
    idclient SERIAL PRIMARY KEY,
    nomclient VARCHAR(100) NOT NULL,
    prenomclient VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    idsite INTEGER REFERENCES site(idsite) ON DELETE SET NULL,
    admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE plageip (
    idplage SERIAL PRIMARY KEY,
    adressedebut INET NOT NULL,
    adressefin INET NOT NULL,
    masque INTEGER NOT NULL,
    idsite INTEGER REFERENCES site(idsite) ON DELETE CASCADE
);

CREATE TABLE vlan (
    idvlan SERIAL PRIMARY KEY,
    numvlan INTEGER NOT NULL UNIQUE, 
    nomvrf VARCHAR(100) NOT NULL,
    rd VARCHAR(50) NOT NULL,
    idclient INTEGER UNIQUE REFERENCES client(idclient) ON DELETE CASCADE
);

CREATE TABLE sousreseau (
    idsousreseau SERIAL PRIMARY KEY,
    ipreseau INET NOT NULL,
    masque INTEGER NOT NULL CHECK (masque = 24),
    ipinterface INET NOT NULL,
    statut VARCHAR(20) DEFAULT 'attribué',
    idclient INTEGER REFERENCES client(idclient) ON DELETE SET NULL
);

INSERT INTO site (nomsite) VALUES
('Paris'),


INSERT INTO client (nomclient, prenomclient, email, mot_de_passe, idsite, admin)
VALUES (
    'Admin', 'Compte', 'admin@gmail.com',
    '$2y$10$sISPziTwQprPp83VMnswmueE3TruWxUbo5t4WBcw7NE7Uir0GLkKa', /*mdp admin -> admin */
    1, TRUE
);
INSERT INTO plageip (idplage, adressedebut, adressefin, masque, idsite)
VALUES (
    1, '164.166.1.0', '164.166.1.255',24,1
);
