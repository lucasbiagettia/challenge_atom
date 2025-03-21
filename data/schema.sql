CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para almacenar detalles adicionales de los leads
CREATE TABLE IF NOT EXISTS lead_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    budget TEXT,
    needs TEXT,
    product_interest TEXT,
    timeline TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Tabla para almacenar conversaciones
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Tabla para almacenar mensajes de la conversación
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    sender TEXT CHECK(sender IN ('agent', 'lead')),
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);