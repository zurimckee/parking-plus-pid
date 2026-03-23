CREATE DATABASE ParkingDB;
USE ParkingDB;

CREATE TABLE Spots(
	Spot_ID MEDIUMINT UNSIGNED UNIQUE,
    Status BOOLEAN NOT NULL DEFAULT TRUE,
    Lot_ID CHAR(4),
    Spot_Type ENUM('Handicapped', 'Staff', 'Reserved'),
    Geometry_ID MEDIUMINT UNSIGNED NOT NULL, 
    Level SMALLINT UNSIGNED,
    PRIMARY KEY (Spot_ID),
    FOREIGN KEY (Lot_ID) REFERENCES Lots(Lot_ID) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);
ALTER TABLE Spots ADD last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

CREATE TABLE Lots(
	Lot_ID CHAR(4) UNIQUE,
    Lot_Name VARCHAR(50) NOT NULL,
    Address VARCHAR(250) NOT NULL UNIQUE,
    Num_Spaces MEDIUMINT UNSIGNED NOT NULL,
    Total_Spaces MEDIUMINT UNSIGNED,
    Is_Active BOOLEAN NOT NULL DEFAULT TRUE,
    Latitude DECIMAL(9,6) UNIQUE,
    Longitude DECIMAL(9,6) UNIQUE,
    Lot_Type ENUM('Deck', 'Lot', 'Street'),
    PRIMARY KEY(Lot_ID)
    );

-- dynamically retrieves data from defined tables whenever its queried by frontend
CREATE VIEW Lot_Status_Summary AS 
SELECT 
	Lot.Lot_ID,
    Lot.Lot_Name,
    Lot.Total_Spaces, 
    COUNT(Spot.Spot_ID) AS Occupied_Count, 
    (Lot.Total_Spaces - COUNT(Spot.Spot_ID)) AS Num_Spaces
FROM Lots Lot
LEFT JOIN Spots Spot ON Lot.Lot_ID = Spot.Lot_ID AND Spot.Status = TRUE
GROUP BY Lot.Lot_ID;

-- GROUPS DATA BY HOUR/DAY/WEEK FOR USAGE TRENDS
CREATE TABLE Occupancy_Logs(
	Log_ID INT AUTO_INCREMENT,
    Spot_ID MEDIUMINT UNSIGNED UNIQUE NOT NULL,
    New_Status BOOLEAN NOT NULL,
    Time_Stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Log_ID),
	FOREIGN KEY(Spot_ID) REFERENCES Spots(Spot_ID)
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);

-- trigger : whenever a row in Spots is updated check the Status col for changes, if so alter occupancy_logs table
DELIMITER //
CREATE TRIGGER Check_Spot_Stat_Update
AFTER UPDATE ON Spots
FOR EACH ROW
BEGIN
	IF OLD.Status <> NEW.Status THEN
		INSERT INTO Occupancy_Logs(Spot_ID, New_Status)
        VALUES(NEW.Spot_ID, NEW.Status);
	END IF;
END //
DELIMITER ;




-- for error logging and system alerts for sensors
CREATE TABLE Sensor_Health(
	Sensor_ID MEDIUMINT UNSIGNED,
    Last_Ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    Is_Online BOOLEAN DEFAULT TRUE,
    FOREIGN KEY(Sensor_ID) REFERENCES Spots(Spot_ID) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);



    
    


SHOW CREATE TABLE Spots;
SHOW CREATE TABLE Lots;
SHOW CREATE TABLE Occupancy_Logs;
SHOW CREATE TABLE Sensor_Health;


