import sqlite3
import os
from datetime import datetime
from src.config import DATABASE_PATH
from src.database.models import Lead, LeadDetails, Conversation, Message


def get_db_connection():
    """Crear una conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Inicializar la base de datos con el esquema definido"""
    conn = get_db_connection()
    try:
        with open('data/schema.sql') as f:
            conn.executescript(f.read())
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


def create_lead(lead: Lead):
    """Crear un nuevo lead en la base de datos"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO leads (name, company, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (lead.name, lead.company, lead.email, lead.phone)
        )
        lead_id = cursor.lastrowid
        conn.commit()
        return lead_id
    finally:
        conn.close()


def update_lead_details(details: LeadDetails):
    """Actualizar o crear detalles de un lead"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Verificar si ya existen detalles para este lead
        cursor.execute("SELECT id FROM lead_details WHERE lead_id = ?", (details.lead_id,))
        existing_id = cursor.fetchone()
        
        if existing_id:
            # Actualizar detalles existentes
            cursor.execute(
                """
                UPDATE lead_details
                SET budget = ?, needs = ?, product_interest = ?, timeline = ?
                WHERE lead_id = ?
                """,
                (details.budget, details.needs, details.product_interest, details.timeline, details.lead_id)
            )
        else:
            # Crear nuevos detalles
            cursor.execute(
                """
                INSERT INTO lead_details (lead_id, budget, needs, product_interest, timeline)
                VALUES (?, ?, ?, ?, ?)
                """,
                (details.lead_id, details.budget, details.needs, details.product_interest, details.timeline)
            )
        
        conn.commit()
    finally:
        conn.close()


def get_lead_by_id(lead_id: int):
    """Obtener un lead por su ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        lead_data = cursor.fetchone()
        
        if lead_data:
            lead = Lead(
                id=lead_data['id'],
                name=lead_data['name'],
                company=lead_data['company'],
                email=lead_data['email'],
                phone=lead_data['phone'],
                created_at=lead_data['created_at']
            )
            return lead
        return None
    finally:
        conn.close()


def get_lead_by_email(email: str):
    """Obtener un lead por su email"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE email = ?", (email,))
        lead_data = cursor.fetchone()
        
        if lead_data:
            lead = Lead(
                id=lead_data['id'],
                name=lead_data['name'],
                company=lead_data['company'],
                email=lead_data['email'],
                phone=lead_data['phone'],
                created_at=lead_data['created_at']
            )
            return lead
        return None
    finally:
        conn.close()


def start_conversation(lead_id: int):
    """Iniciar una nueva conversación con un lead"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (lead_id, started_at)
            VALUES (?, ?)
            """,
            (lead_id, datetime.now())
        )
        conversation_id = cursor.lastrowid
        conn.commit()
        return conversation_id
    finally:
        conn.close()


def end_conversation(conversation_id: int):
    """Finalizar una conversación"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE conversations
            SET ended_at = ?
            WHERE id = ?
            """,
            (datetime.now(), conversation_id)
        )
        conn.commit()
    finally:
        conn.close()


def add_message(message: Message):
    """Añadir un mensaje a una conversación"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender, content, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (message.conversation_id, message.sender, message.content, message.timestamp)
        )
        message_id = cursor.lastrowid
        conn.commit()
        return message_id
    finally:
        conn.close()


def get_conversation_messages(conversation_id: int):
    """Obtener todos los mensajes de una conversación"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp
            """,
            (conversation_id,)
        )
        messages_data = cursor.fetchall()
        
        messages = []
        for msg_data in messages_data:
            message = Message(
                id=msg_data['id'],
                conversation_id=msg_data['conversation_id'],
                sender=msg_data['sender'],
                content=msg_data['content'],
                timestamp=msg_data['timestamp']
            )
            messages.append(message)
        
        return messages
    finally:
        conn.close()