-- Recreate tables for chatbot_armaddia
USE chatbot_armaddia;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sellers table
CREATE TABLE sellers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    territory VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(100),
    confidence FLOAT,
    context_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    seller_id INT,
    FOREIGN KEY (seller_id) REFERENCES sellers(id)
);

-- Chat reports table
CREATE TABLE chat_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    message_count INT DEFAULT 0,
    last_interaction TIMESTAMP,
    intent_summary JSON,
    satisfaction_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO sellers (name, email, phone, territory) VALUES 
('Carlos Rodriguez', 'carlos@gpscontrol.mx', '+525512345678', 'Ciudad de Mexico'),
('Maria Gonzalez', 'maria@gpscontrol.mx', '+525587654321', 'Guadalajara'),
('Juan Perez', 'juan@gpscontrol.mx', '+525599887766', 'Monterrey');

INSERT INTO users (username, password_hash, email, role) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeVMskdliMHW8O/O2', 'admin@armaddia.lat', 'admin');

-- Show created tables
SHOW TABLES;