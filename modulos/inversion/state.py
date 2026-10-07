"""
state.py — Gestión centralizada del estado de sesión para el módulo de Inversión Inicial.

Estructura en st.session_state["inversion_activos"]:
[
    {
        "ficha": { ...campos ficha técnica... },
        "presupuestos": [
            { ...datos proveedor 1... },
            { ...datos proveedor 2... },
            { ...datos proveedor 3... },
        ],
        "proveedor_sel": {
            "idx": int,        # índice 0-2 del proveedor elegido
            "criterio": str    # justificación de selección
        } | None
    },
    ...
]
"""

import streamlit as st

INVERSION_STATE_KEY = "inversion_activos"


def _init():
    """Inicializa la lista de activos en sesión si aún no existe."""
    if INVERSION_STATE_KEY not in st.session_state:
        st.session_state[INVERSION_STATE_KEY] = []


def get_activos() -> list:
    """Retorna la lista completa de activos registrados en la sesión actual."""
    _init()
    return st.session_state[INVERSION_STATE_KEY]


def agregar_activo(ficha: dict) -> int:
    """
    Agrega un nuevo activo a la sesión.
    Retorna el índice asignado al activo dentro de la lista.
    """
    _init()
    st.session_state[INVERSION_STATE_KEY].append({
        "ficha": ficha,
        "presupuestos": [],
        "proveedor_sel": None,
    })
    return len(st.session_state[INVERSION_STATE_KEY]) - 1


def actualizar_ficha(idx: int, ficha: dict):
    """Actualiza la ficha técnica de un activo existente."""
    _init()
    activos = st.session_state[INVERSION_STATE_KEY]
    if 0 <= idx < len(activos):
        activos[idx]["ficha"] = ficha


def eliminar_activo(idx: int):
    """Elimina el activo en la posición idx."""
    _init()
    activos = st.session_state[INVERSION_STATE_KEY]
    if 0 <= idx < len(activos):
        activos.pop(idx)


def actualizar_presupuestos(idx_activo: int, presupuestos: list):
    """
    Guarda la lista de presupuestos (máx. 3) para el activo en idx_activo.
    Cada presupuesto es un dict con los campos del proveedor y los cálculos.
    """
    _init()
    activos = st.session_state[INVERSION_STATE_KEY]
    if 0 <= idx_activo < len(activos):
        activos[idx_activo]["presupuestos"] = presupuestos


def seleccionar_proveedor(idx_activo: int, idx_prov: int, criterio: str):
    """
    Registra la selección del proveedor para el activo dado.
    idx_prov: índice 0-2 dentro de la lista de presupuestos del activo.
    """
    _init()
    activos = st.session_state[INVERSION_STATE_KEY]
    if 0 <= idx_activo < len(activos):
        activos[idx_activo]["proveedor_sel"] = {
            "idx": idx_prov,
            "criterio": criterio,
        }


def get_inversion_total() -> float:
    """
    Calcula el monto total de inversión sumando los Total DDP
    de los proveedores seleccionados en cada activo.
    Activos sin proveedor seleccionado aportan $0.
    """
    _init()
    total = 0.0
    for activo in st.session_state[INVERSION_STATE_KEY]:
        sel = activo.get("proveedor_sel")
        presupuestos = activo.get("presupuestos", [])
        if sel is not None:
            idx_p = sel.get("idx", -1)
            if 0 <= idx_p < len(presupuestos):
                unidades = activo["ficha"].get("unidades", 1)
                total_ddp = presupuestos[idx_p].get("total_ddp", 0.0)
                total += total_ddp * unidades
    return round(total, 2)


def reset_inversion():
    """Limpia todos los activos y presupuestos de la sesión."""
    st.session_state[INVERSION_STATE_KEY] = []
