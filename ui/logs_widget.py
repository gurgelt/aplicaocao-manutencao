#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação do widget de logs e usuários online para o Sistema de Manutenção.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QTableWidget, QTableWidgetItem, QHeaderView, 
                           QPushButton, QSplitter)
from PyQt5.QtCore import Qt

class TelaLogs(QWidget):
    """Classe para o widget de visualização de logs e usuários online."""
    
    def __init__(self, db):
        """Inicializa o widget de logs."""
        super().__init__()
        self.db = db
        self.init_ui()
        self.atualizar_dados()
    
    def init_ui(self):
        """Configura a interface de usuário."""
        layout = QVBoxLayout(self)
        
        # Splitter para dividir logs e usuários online
        splitter = QSplitter(Qt.Vertical)
        
        # Grupo de usuários online
        online_group = QGroupBox("Usuários Online")
        online_layout = QVBoxLayout()
        
        self.online_table = QTableWidget()
        self.online_table.setColumnCount(2)
        self.online_table.setHorizontalHeaderLabels(["Nome", "Usuário"])
        self.online_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.online_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        online_layout.addWidget(self.online_table)
        online_group.setLayout(online_layout)
        
        # Grupo de logs
        logs_group = QGroupBox("Logs de Ações")
        logs_layout = QVBoxLayout()
        
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(["Usuário", "Ação", "Descrição", "Data/Hora"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        logs_layout.addWidget(self.logs_table)
        logs_group.setLayout(logs_layout)
        
        # Adicionar grupos ao splitter
        splitter.addWidget(online_group)
        splitter.addWidget(logs_group)
        
        # Botão de atualizar
        atualizar_btn = QPushButton("Atualizar Dados")
        atualizar_btn.clicked.connect(self.atualizar_dados)
        
        layout.addWidget(splitter)
        layout.addWidget(atualizar_btn)
    
    def atualizar_dados(self):
        """Atualiza os dados de usuários online e logs do sistema."""
        # Atualizar usuários online
        usuarios_online = self.db.obter_usuarios_online()
        self.online_table.setRowCount(0)
        
        for row_idx, usuario in enumerate(usuarios_online):
            nome, username = usuario
            
            self.online_table.insertRow(row_idx)
            self.online_table.setItem(row_idx, 0, QTableWidgetItem(nome))
            self.online_table.setItem(row_idx, 1, QTableWidgetItem(username))
        
        # Atualizar logs
        logs = self.db.obter_logs()
        self.logs_table.setRowCount(0)
        
        for row_idx, log in enumerate(logs):
            nome_usuario, acao, descricao, data_hora = log
            
            self.logs_table.insertRow(row_idx)
            self.logs_table.setItem(row_idx, 0, QTableWidgetItem(nome_usuario))
            self.logs_table.setItem(row_idx, 1, QTableWidgetItem(acao))
            self.logs_table.setItem(row_idx, 2, QTableWidgetItem(descricao))
            self.logs_table.setItem(row_idx, 3, QTableWidgetItem(data_hora))