"""Crea tienda.db con clientes, productos y ventas de ejemplo."""
import random
import sqlite3
from datetime import date, timedelta

CLIENTES = ["Ferretería Lima", "Bodega Don Lucho", "Minimarket Sol", "Distribuidora Andina", "Tienda Rosita"]
PRODUCTOS = [("Arroz 5 kg", 24.5), ("Aceite 1 L", 11.9), ("Azúcar 1 kg", 4.8), ("Leche 400 g", 4.2), ("Fideos 500 g", 3.5)]


def crear(ruta="tienda.db"):
    random.seed(7)
    conn = sqlite3.connect(ruta)
    conn.executescript("""
        DROP TABLE IF EXISTS ventas; DROP TABLE IF EXISTS clientes; DROP TABLE IF EXISTS productos;
        CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT);
        CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL);
        CREATE TABLE ventas (id INTEGER PRIMARY KEY, cliente_id INTEGER REFERENCES clientes,
                             producto_id INTEGER REFERENCES productos, cantidad INTEGER, fecha TEXT);
    """)
    conn.executemany("INSERT INTO clientes (nombre) VALUES (?)", [(c,) for c in CLIENTES])
    conn.executemany("INSERT INTO productos (nombre, precio) VALUES (?, ?)", PRODUCTOS)
    inicio = date(2026, 1, 1)
    conn.executemany(
        "INSERT INTO ventas (cliente_id, producto_id, cantidad, fecha) VALUES (?, ?, ?, ?)",
        [(random.randint(1, 5), random.randint(1, 5), random.randint(1, 40),
          str(inicio + timedelta(days=random.randint(0, 180)))) for _ in range(500)],
    )
    conn.commit()
