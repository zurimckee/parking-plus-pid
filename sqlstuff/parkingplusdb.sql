CREATE DATABASE ParkingDB;
USE ParkingDB;

-- TABLES --

CREATE TABLE Spots(
	Spot_ID MEDIUMINT UNSIGNED UNIQUE,
    Status BOOLEAN NOT NULL DEFAULT TRUE,
    Lot_ID CHAR(4),
    Spot_Type ENUM('Handicapped', 'Staff', 'Reserved'),
    Level SMALLINT UNSIGNED,
    PRIMARY KEY (Spot_ID),
    FOREIGN KEY (Lot_ID) REFERENCES Lots(Lot_ID) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);

SELECT Spot_ID, Lot_ID FROM Spots;
ALTER TABLE Spots ADD last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
ALTER TABLE Spots DROP INDEX Spot_ID; 
ALTER TABLE Spots DROP Geometry_ID;


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
SELECT Address FROM Lots;


-- GROUPS DATA BY HOUR/DAY/WEEK FOR USAGE TRENDS
CREATE TABLE Occupancy_Logs(
	Log_ID INT AUTO_INCREMENT,
    Spot_ID MEDIUMINT UNSIGNED NOT NULL,
    New_Status BOOLEAN NOT NULL,
    Time_Stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Log_ID),
	FOREIGN KEY(Spot_ID) REFERENCES Spots(Spot_ID)
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);
	

-- for error logging and system alerts for sensors
CREATE TABLE Sensor_Health(
	Sensor_ID MEDIUMINT UNSIGNED,
    Last_Ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    Is_Online BOOLEAN DEFAULT TRUE,
    FOREIGN KEY(Sensor_ID) REFERENCES Spots(Spot_ID) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);

INSERT INTO Sensor_Health (Sensor_ID, Last_Ping, Is_Online) VALUES
(1001, NOW(), TRUE),
(1002, NOW(), TRUE),
(1003, DATE_SUB(NOW(), INTERVAL 15 MINUTE), FALSE),  -- stale/dead
(2001, NOW(), TRUE),
(2002, DATE_SUB(NOW(), INTERVAL 2 MINUTE), TRUE),
(3001, NOW(), TRUE),
(3002, DATE_SUB(NOW(), INTERVAL 45 MINUTE), FALSE),  -- offline
(4001, NOW(), TRUE),
(5001, DATE_SUB(NOW(), INTERVAL 1 HOUR), FALSE);     -- offline (inactive lot)


-- INSERTS --
INSERT INTO Spots (Spot_ID, Status, Lot_ID, Spot_Type, Geometry_ID, Level) VALUES
-- L001 Main Street Deck (155 occupied, 45 free)
(1001, FALSE, 'L001', 'Staff', 1, 1),
(1002, FALSE, 'L001', 'Reserved', 2, 1),
(1003, TRUE,  'L001', 'Handicapped', 3, 1),
(1004, FALSE, 'L001', 'Staff', 4, 2),
(1005, TRUE,  'L001', 'Reserved', 5, 2),
(1006, FALSE, 'L001', NULL, 6, 2),
(1007, FALSE, 'L001', NULL, 7, 3),
(1008, TRUE,  'L001', NULL, 8, 3),

-- L002 Uptown Surface Lot (63 occupied, 12 free)
(2001, FALSE, 'L002', 'Handicapped', 9, 1),
(2002, FALSE, 'L002', 'Staff', 10, 1),
(2003, TRUE,  'L002', NULL, 11, 1),
(2004, FALSE, 'L002', NULL, 12, 1),
(2005, TRUE,  'L002', 'Reserved', 13, 1),

-- L003 South End Garage (220 occupied, 80 free)
(3001, FALSE, 'L003', 'Staff', 14, 1),
(3002, FALSE, 'L003', 'Reserved', 15, 1),
(3003, FALSE, 'L003', 'Handicapped', 16, 2),
(3004, TRUE,  'L003', NULL, 17, 2),
(3005, FALSE, 'L003', NULL, 18, 3),
(3006, TRUE,  'L003', NULL, 19, 3),
(3007, FALSE, 'L003', NULL, 20, 4),

-- L004 Central Ave Street (17 occupied, 3 free)
(4001, FALSE, 'L004', NULL, 21, 1),
(4002, FALSE, 'L004', 'Handicapped', 22, 1),
(4003, TRUE,  'L004', NULL, 23, 1),

-- L005 NoDa Lot (inactive, 30 occupied)
(5001, FALSE, 'L005', NULL, 24, 1),
(5002, FALSE, 'L005', 'Staff', 25, 1),
(5003, TRUE,  'L005', NULL, 26, 1);

INSERT INTO Lots (Lot_ID, Lot_Name, Address, Num_Spaces, Total_Spaces, Is_Active, Latitude, Longitude, Lot_Type) VALUES
('L001', 'Main Street Deck', '123 Main St, Charlotte, NC 28202', 45, 200, TRUE, 35.227085, -80.843124, 'Deck'),
('L002', 'Uptown Surface Lot', '456 Tryon St, Charlotte, NC 28202', 12, 75, TRUE, 35.228910, -80.841200, 'Lot'),
('L003', 'South End Garage', '789 South Blvd, Charlotte, NC 28203', 80, 300, TRUE, 35.214500, -80.855300, 'Deck'),
('L004', 'Central Ave Street', '321 Central Ave, Charlotte, NC 28205', 3, 20, TRUE, 35.221300, -80.820400, 'Street'),
('L005', 'NoDa Lot', '900 36th St, Charlotte, NC 28205', 30, 60, FALSE, 35.245600, -80.812300, 'Lot');

INSERT INTO Occupancy_Logs (Spot_ID, New_Status, Time_Stamp) VALUES
-- today's activity
(1001, FALSE, DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(1002, FALSE, DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(1003, TRUE,  DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(2001, FALSE, DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(3001, FALSE, DATE_SUB(NOW(), INTERVAL 4 HOUR)),
(3002, TRUE,  DATE_SUB(NOW(), INTERVAL 5 HOUR)),
(4001, FALSE, DATE_SUB(NOW(), INTERVAL 6 HOUR)),

-- yesterday
(1001, TRUE,  DATE_SUB(NOW(), INTERVAL 1 DAY)),
(2002, FALSE, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(3003, FALSE, DATE_SUB(NOW(), INTERVAL 1 DAY)),

-- 2 days ago
(1004, FALSE, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(2003, TRUE,  DATE_SUB(NOW(), INTERVAL 2 DAY)),
(3005, FALSE, DATE_SUB(NOW(), INTERVAL 2 DAY)),

-- 3 days ago
(1006, FALSE, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(2004, FALSE, DATE_SUB(NOW(), INTERVAL 3 DAY)),

-- 5 days ago
(1007, FALSE, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3007, TRUE,  DATE_SUB(NOW(), INTERVAL 5 DAY)),

-- last week
(1002, TRUE,  DATE_SUB(NOW(), INTERVAL 7 DAY)),
(2001, TRUE,  DATE_SUB(NOW(), INTERVAL 7 DAY)),
(3001, TRUE,  DATE_SUB(NOW(), INTERVAL 7 DAY));


-- VIEWS --
CREATE VIEW Spot_Status_Summary AS 
SELECT  
	l.Lot_Name,
	s.Spot_Type,
	COUNT(*) AS Count
FROM Spots s
JOIN Lots l ON s.Lot_ID = l.Lot_ID
WHERE s.Spot_Type IS NOT NULL
GROUP BY l.Lot_Name, s.Spot_Type;


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

CREATE VIEW Near_Capacity AS
SELECT
	Lot_Name, 
    Total_Spaces,
    Num_Spaces AS Available,
    ROUND((Occupied_Count / Total_Spaces) * 100, 1) AS Occupancy_Perc
FROM Lot_Status_Summary
WHERE (Occupied_Count / Total_Spaces) >= 0.8
ORDER BY Occupancy_Perc DESC;

CREATE VIEW Hourly_Occupancy AS
SELECT 
    HOUR(Time_Stamp)                                       AS `Hour`,
    COUNT(*)                                               AS `Events`,
    SUM(CASE WHEN New_Status = FALSE THEN 1 ELSE 0 END)   AS `Occupancies`,
    SUM(CASE WHEN New_Status = TRUE  THEN 1 ELSE 0 END)   AS `Departures`
FROM Occupancy_Logs
WHERE DATE(Time_Stamp) = CURDATE()
GROUP BY HOUR(Time_Stamp)
ORDER BY `Hour`;

CREATE VIEW Daily_Occupancy AS 
SELECT
	DATE(Time_Stamp) AS Day,
	COUNT(*) AS Events,
    SUM(CASE WHEN New_Status = FALSE THEN 1 ELSE 0 END) AS Occupancies,
    SUM(CASE WHEN New_Status = TRUE THEN 1 ELSE 0 END) AS Departures
FROM Occupancy_Logs
WHERE Time_Stamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY DATE(Time_Stamp)
ORDER BY Day;

CREATE VIEW Peak_Occupancy AS 
SELECT 
    HOUR(Time_Stamp) AS Hour,
    COUNT(*) AS Occupancy_Events
FROM Occupancy_Logs
WHERE New_Status = FALSE
GROUP BY HOUR(Time_Stamp)
ORDER BY Occupancy_Events DESC;


-- TRIGGERS -- 
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

    


SHOW CREATE TABLE Spots;
SELECT * FROM Spots;
SHOW CREATE TABLE Lots;
SELECT * FROM Lots;
SHOW CREATE TABLE Occupancy_Logs;
SELECT * FROM Occupancy_Logs;
SHOW CREATE TABLE Sensor_Health;
SELECT * FROM Sensor_Health;




