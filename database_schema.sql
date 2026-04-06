-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    vin TEXT,
    make TEXT,
    model TEXT,
    year INTEGER,
    license_plate TEXT,
    mileage INTEGER DEFAULT 0,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Diagnostics table (enhanced)
CREATE TABLE IF NOT EXISTS diagnostics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    diagnostic_type TEXT,
    symptoms TEXT,
    results TEXT,
    severity TEXT,
    tools TEXT,
    action_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    technician TEXT,
    notes TEXT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'technician',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
