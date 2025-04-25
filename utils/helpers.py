#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Funções auxiliares para o Sistema de Manutenção.
"""

import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

def validar_email(email):
    """
    Valida se uma string está em formato de e-mail válido.
    
    Args:
        email (str): String com o e-mail para validar
        
    Returns:
        bool: True se o e-mail for válido, False caso contrário
    """
    # Padrão simples para validação de e-mail
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))

def colorir_tabela_por_prioridade(tabela, row_idx, prioridade):
    """
    Aplica cor de fundo a uma linha da tabela baseado na prioridade.
    
    Args:
        tabela (QTableWidget): Tabela a ser colorida
        row_idx (int): Índice da linha
        prioridade (str): Prioridade da solicitação ('Baixa', 'Normal', 'Alta', 'Urgente')
        
    Returns:
        None
    """
    # Definir cor base pela prioridade
    if prioridade == "Baixa":
        cor = Qt.white
    elif prioridade == "Normal":
        cor = Qt.lightGray
    elif prioridade == "Alta":
        cor = Qt.yellow
    else:  # Urgente
        cor = QColor(255, 200, 200)  # Vermelho mais suave
    
    # Aplicar cor a todas as colunas da linha
    for col in range(tabela.columnCount()):
        tabela.item(row_idx, col).setBackground(cor)

def colorir_tabela_por_status(tabela, row_idx, status, prioridade):
    """
    Aplica cor de fundo a uma linha da tabela baseado no status,
    com prioridade sobre a cor da prioridade.
    
    Args:
        tabela (QTableWidget): Tabela a ser colorida
        row_idx (int): Índice da linha
        status (str): Status da solicitação
        prioridade (str): Prioridade da solicitação (caso o status não tenha cor específica)
        
    Returns:
        None
    """
    # Definir a cor base pela prioridade
    if prioridade == "Baixa":
        cor_base = Qt.white
    elif prioridade == "Normal":
        cor_base = Qt.lightGray
    elif prioridade == "Alta":
        cor_base = Qt.yellow
    else:  # Urgente
        cor_base = QColor(255, 200, 200)  # Vermelho mais suave
    
    # Sobrescrever com cor de status se for status especial
    if status == "Concluído":
        cor_base = QColor(200, 255, 200)  # Verde claro
    elif status == "Cancelado":
        cor_base = QColor(220, 220, 220)  # Cinza mais escuro
    elif status == "Em manutenção":
        cor_base = QColor(200, 200, 255)  # Azul claro
    elif status == "Orçamento aprovado":
        cor_base = QColor(255, 240, 200)  # Amarelo claro
    
    # Aplicar cor à linha
    for col in range(tabela.columnCount()):
        tabela.item(row_idx, col).setBackground(cor_base)