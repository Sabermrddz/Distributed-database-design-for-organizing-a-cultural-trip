-- ============================================================
-- DISTRIBUTED CULTURAL TRIP DATABASE SCHEMA
-- ============================================================
-- Run as: north_user on north-db
-- Run as: south_user on south-db
-- Run as: east_user  on east-db
-- Run as: central_user on central-db
-- ============================================================


-- ============================================================
-- PART 1: REGIONAL TABLES (run on each regional node)
-- north_user / south_user / east_user
-- ============================================================

CREATE TABLE Trips (
    TripID      NUMBER PRIMARY KEY,
    Region      NVARCHAR2(50),
    StartDate   DATE,
    EndDate     DATE
);

CREATE TABLE Guides (
    GuideID     NUMBER PRIMARY KEY,
    Name        NVARCHAR2(100),
    Region      NVARCHAR2(50),
    Languages   NVARCHAR2(100)
);

CREATE TABLE Accommodations (
    HotelID     NUMBER PRIMARY KEY,
    Name        NVARCHAR2(100),
    Region      NVARCHAR2(50),
    Rating      NUMBER
);

CREATE TABLE CulturalEvents (
    EventID     NUMBER PRIMARY KEY,
    Region      NVARCHAR2(50),
    Name        NVARCHAR2(100),
    EventDate   DATE,
    Type        NVARCHAR2(50)
);


-- ============================================================
-- PART 2: SAMPLE DATA — north_user (north-db)
-- ============================================================

INSERT INTO Trips VALUES (101, 'North', DATE '2025-06-01', DATE '2025-06-10');
INSERT INTO Guides VALUES (301, 'Nasser Samir', 'North', 'Arabic, French');
INSERT INTO Accommodations VALUES (501, 'El Aurassi Hotel', 'North', 5);
INSERT INTO CulturalEvents VALUES (401, 'North', 'Timgad Festival', DATE '2025-06-05', 'Music');
COMMIT;


-- ============================================================
-- PART 3: SAMPLE DATA — south_user (south-db)
-- ============================================================

INSERT INTO Trips VALUES (102, 'South', DATE '2025-07-05', DATE '2025-07-15');
INSERT INTO Guides VALUES (302, 'Hadj Moussa', 'South', 'Arabic, Tamazight');
INSERT INTO Accommodations VALUES (502, 'Hotel Tahat', 'South', 4);
INSERT INTO CulturalEvents VALUES (402, 'South', 'Tamanrasset Festival', DATE '2025-07-10', 'Heritage');
COMMIT;


-- ============================================================
-- PART 4: SAMPLE DATA — east_user (east-db)
-- ============================================================

INSERT INTO Trips VALUES (103, 'East', DATE '2025-08-01', DATE '2025-08-10');
INSERT INTO Guides VALUES (303, 'Omar Ben Ali', 'East', 'Arabic, French');
INSERT INTO Accommodations VALUES (503, 'Hotel Chiak', 'East', 4);
INSERT INTO CulturalEvents VALUES (403, 'East', 'Batna Festival', DATE '2025-08-05', 'Culture');
COMMIT;


-- ============================================================
-- PART 5: CENTRAL TABLES — central_user (central-db)
-- ============================================================

-- Vertical Fragmentation of Tourists
CREATE TABLE Tourist_Basic (
    TouristID   NUMBER PRIMARY KEY,
    Name        NVARCHAR2(100)
);

CREATE TABLE Tourist_Contact (
    TouristID   NUMBER PRIMARY KEY,
    Nationality NVARCHAR2(50),
    Contact     NVARCHAR2(50)
);

-- Mixed Fragmentation of Bookings
CREATE TABLE Booking_Info (
    BookingID   NUMBER PRIMARY KEY,
    TouristID   NUMBER,
    TripID      NUMBER
);

CREATE TABLE Booking_Amount (
    BookingID   NUMBER PRIMARY KEY,
    Amount      NUMBER,
    LastUpdated DATE
);


-- ============================================================
-- PART 6: SAMPLE DATA — central_user
-- ============================================================

INSERT INTO Tourist_Basic VALUES (1, 'Ahmed Ben Mohamed');
INSERT INTO Tourist_Basic VALUES (2, 'Mansouri Leila');
INSERT INTO Tourist_Basic VALUES (3, 'Karim Bouaziz');

INSERT INTO Tourist_Contact VALUES (1, 'Algerian', '0550123456');
INSERT INTO Tourist_Contact VALUES (2, 'Tunisian', '002169876543');
INSERT INTO Tourist_Contact VALUES (3, 'Algerian', '0661234567');

INSERT INTO Booking_Info VALUES (201, 1, 101);
INSERT INTO Booking_Info VALUES (202, 2, 102);
INSERT INTO Booking_Info VALUES (203, 3, 103);

INSERT INTO Booking_Amount VALUES (201, 80000, SYSDATE);
INSERT INTO Booking_Amount VALUES (202, 75000, SYSDATE);
INSERT INTO Booking_Amount VALUES (203, 90000, SYSDATE);

COMMIT;


-- ============================================================
-- PART 7: DB LINKS — central_user
-- ============================================================

CREATE DATABASE LINK north_link
    CONNECT TO north_user IDENTIFIED BY north_pass
    USING '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=10.110.0.3)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))';

CREATE DATABASE LINK south_link
    CONNECT TO south_user IDENTIFIED BY south_pass
    USING '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=10.110.0.4)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))';

CREATE DATABASE LINK east_link
    CONNECT TO east_user IDENTIFIED BY east_pass
    USING '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=10.110.0.5)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=XEPDB1)))';


-- ============================================================
-- PART 8: GLOBAL VIEWS — central_user
-- ============================================================

-- Horizontal Fragmentation Views (from 3 nodes)
CREATE VIEW All_Trips AS
    SELECT * FROM Trips@north_link
    UNION
    SELECT * FROM Trips@south_link
    UNION
    SELECT * FROM Trips@east_link;

CREATE VIEW All_Guides AS
    SELECT * FROM Guides@north_link
    UNION
    SELECT * FROM Guides@south_link
    UNION
    SELECT * FROM Guides@east_link;

CREATE VIEW All_Accommodations AS
    SELECT * FROM Accommodations@north_link
    UNION
    SELECT * FROM Accommodations@south_link
    UNION
    SELECT * FROM Accommodations@east_link;

CREATE VIEW All_Events AS
    SELECT * FROM CulturalEvents@north_link
    UNION
    SELECT * FROM CulturalEvents@south_link
    UNION
    SELECT * FROM CulturalEvents@east_link;

-- Vertical Fragmentation View (Tourist_Basic + Tourist_Contact)
CREATE VIEW All_Tourists AS
    SELECT tb.TouristID, tb.Name, tc.Nationality, tc.Contact
    FROM Tourist_Basic tb
    JOIN Tourist_Contact tc ON tb.TouristID = tc.TouristID;

-- Mixed Fragmentation View (Booking_Info + Booking_Amount)
CREATE VIEW Booking_Full AS
    SELECT bi.BookingID, bi.TouristID, bi.TripID, ba.Amount, ba.LastUpdated
    FROM Booking_Info bi
    JOIN Booking_Amount ba ON bi.BookingID = ba.BookingID;

-- Combined View (Booking + Tourist + Trip)
CREATE VIEW Booking_Details AS
    SELECT bf.BookingID, at.Name AS TouristName, atr.Region,
           atr.StartDate, atr.EndDate, bf.Amount
    FROM Booking_Full bf
    JOIN All_Tourists at ON bf.TouristID = at.TouristID
    JOIN All_Trips atr ON bf.TripID = atr.TripID;

-- Full Itinerary View (everything combined)
CREATE VIEW Full_Itinerary AS
    SELECT bf.BookingID, at.Name AS TouristName, at.Nationality,
           atr.Region, atr.StartDate, atr.EndDate, bf.Amount,
           ae.Name AS EventName, ae.EventDate,
           ag.Name AS GuideName, ag.Languages
    FROM Booking_Full bf
    JOIN All_Tourists at ON bf.TouristID = at.TouristID
    JOIN All_Trips atr ON bf.TripID = atr.TripID
    JOIN All_Events ae ON atr.Region = ae.Region
    JOIN All_Guides ag ON atr.Region = ag.Region;


-- ============================================================
-- PART 9: PL/SQL PROCEDURE — central_user
-- ============================================================

CREATE OR REPLACE PROCEDURE Generate_Itinerary(p_TouristID NUMBER) AS
    v_Name      NVARCHAR2(100);
    v_Region    NVARCHAR2(50);
    v_Start     DATE;
    v_End       DATE;
    v_Guide     NVARCHAR2(100);
    v_Event     NVARCHAR2(100);
    v_Amount    NUMBER;
BEGIN
    SELECT Name INTO v_Name
    FROM Tourist_Basic WHERE TouristID = p_TouristID;

    SELECT atr.Region, atr.StartDate, atr.EndDate, bf.Amount
    INTO v_Region, v_Start, v_End, v_Amount
    FROM Booking_Full bf
    JOIN All_Trips atr ON bf.TripID = atr.TripID
    WHERE bf.TouristID = p_TouristID;

    SELECT Name INTO v_Guide
    FROM All_Guides WHERE Region = v_Region AND ROWNUM = 1;

    SELECT Name INTO v_Event
    FROM All_Events WHERE Region = v_Region AND ROWNUM = 1;

    DBMS_OUTPUT.PUT_LINE('=== Travel Itinerary ===');
    DBMS_OUTPUT.PUT_LINE('Tourist : ' || v_Name);
    DBMS_OUTPUT.PUT_LINE('Region  : ' || v_Region);
    DBMS_OUTPUT.PUT_LINE('From    : ' || TO_CHAR(v_Start, 'DD-MM-YYYY'));
    DBMS_OUTPUT.PUT_LINE('To      : ' || TO_CHAR(v_End,   'DD-MM-YYYY'));
    DBMS_OUTPUT.PUT_LINE('Amount  : ' || v_Amount || ' DZD');
    DBMS_OUTPUT.PUT_LINE('Guide   : ' || v_Guide);
    DBMS_OUTPUT.PUT_LINE('Event   : ' || v_Event);
    DBMS_OUTPUT.PUT_LINE('=======================');
END;
/


-- ============================================================
-- PART 10: CONFLICT RESOLUTION TRIGGER — central_user
-- ============================================================

CREATE OR REPLACE TRIGGER trg_booking_timestamp
BEFORE UPDATE ON Booking_Amount
FOR EACH ROW
BEGIN
    :NEW.LastUpdated := SYSDATE;
END;
/


-- ============================================================
-- TEST QUERIES
-- ============================================================

-- Test DB Links
SELECT * FROM Trips@north_link;
SELECT * FROM Trips@south_link;
SELECT * FROM Trips@east_link;

-- Test Views
SELECT * FROM All_Trips;
SELECT * FROM All_Tourists;
SELECT * FROM Booking_Details;
SELECT * FROM Full_Itinerary;

-- Test Procedure
SET SERVEROUTPUT ON;
EXEC Generate_Itinerary(1);
EXEC Generate_Itinerary(2);
EXEC Generate_Itinerary(3);

-- Test Conflict Resolution
UPDATE Booking_Amount SET Amount = 85000 WHERE BookingID = 201;
COMMIT;
UPDATE Booking_Amount SET Amount = 90000 WHERE BookingID = 201;
COMMIT;
SELECT * FROM Booking_Amount WHERE BookingID = 201;
-- Expected: Amount = 90000, LastUpdated = today
