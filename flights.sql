-- Database structure for flight booking system
-- Integrates with existing shopping cart system

-- Flights table
CREATE TABLE IF NOT EXISTS flights (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_code VARCHAR(10) NOT NULL,
    departure_airport VARCHAR(100) NOT NULL,
    arrival_airport VARCHAR(100) NOT NULL,
    departure_city VARCHAR(50) NOT NULL,
    arrival_city VARCHAR(50) NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    duration VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    available_seats INT NOT NULL,
    aircraft_type VARCHAR(50),
    frequency VARCHAR(50) DEFAULT 'Daily',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_flight_route ON flights(departure_city, arrival_city);
CREATE INDEX IF NOT EXISTS idx_flight_price ON flights(price);
CREATE INDEX IF NOT EXISTS idx_flight_dates ON flights(departure_time, arrival_time);

-- Sample data for popular routes (matching the HTML display)
INSERT INTO flights (flight_code, departure_airport, arrival_airport, departure_city, arrival_city, departure_time, arrival_time, duration, price, available_seats, aircraft_type, frequency) VALUES
('VN123', 'HAN', 'DAD', 'Hà Nội', 'Đà Nẵng', '08:00:00', '09:45:00', '1h 45m', 850000, 150, 'Airbus A321', 'Daily'),
('VN456', 'SGN', 'HAN', 'Hồ Chí Minh', 'Hà Nội', '07:30:00', '09:40:00', '2h 10m', 1200000, 180, 'Boeing 787', 'Daily'),
('VN789', 'HAN', 'PQC', 'Hà Nội', 'Phú Quốc', '09:00:00', '11:30:00', '2h 30m', 1800000, 120, 'Airbus A321neo', 'Daily'),
('VN012', 'DAD', 'CXR', 'Đà Nẵng', 'Nha Trang', '10:15:00', '11:30:00', '1h 15m', 650000, 100, 'ATR 72', 'Daily');

-- Bookings table (to integrate with shopping cart system)
CREATE TABLE IF NOT EXISTS flight_bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_reference VARCHAR(20) UNIQUE NOT NULL,
    user_id INT, -- Reference to users table in existing system
    flight_id INT NOT NULL,
    passenger_count INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    travel_date DATE NOT NULL,
    return_flight_id INT NULL, -- For round trips
    status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    special_requests TEXT,
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    FOREIGN KEY (return_flight_id) REFERENCES flights(id)
);

-- Indexes for bookings
CREATE INDEX IF NOT EXISTS idx_booking_user ON flight_bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_booking_flight ON flight_bookings(flight_id);
CREATE INDEX IF NOT EXISTS idx_booking_reference ON flight_bookings(booking_reference);
CREATE INDEX IF NOT EXISTS idx_booking_date ON flight_bookings(travel_date);

-- Note: To integrate with existing shopping cart system:
-- 1. When user selects a flight and proceeds to booking, create a pending booking
-- 2. Add flight details to shopping cart as a line item
-- 3. On checkout, convert pending booking to confirmed and process payment
-- 4. The booking_reference can be used as the cart item identifier