#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação da janela principal do Sistema de Manutenção.
Esta classe gerencia as abas e a navegação entre diferentes telas.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, 
                            QTabWidget)
from PyQt5.QtCore import Qt

# Importações circulares são tratadas importando dentro da função onde são usadas
# Ver exemplo no método abrir_gerenciar_usuarios

class MainWindow(QMainWindow):
    """Classe para a janela principal com navegação por abas."""
    
    def __init__(self, db, usuario_id, nome_usuario, cargo):
        """Inicializa a janela principal."""
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.nome_usuario = nome_usuario
        self.cargo = cargo
        self.init_ui()
    
    def init_ui(self):
        """Configura a interface de usuário."""
        self.setWindowTitle(f"Sistema de Manutenção - {self.nome_usuario} ({self.cargo})")
        self.setMinimumSize(1000, 600)
        
        # Widget central com abas
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Barra superior
        top_bar = QHBoxLayout()
        
        # Botão de usuários (apenas para admin)
        if self.cargo == "Administrador":
            usuarios_btn = QPushButton("Gerenciar Usuários")
            usuarios_btn.clicked.connect(self.abrir_gerenciar_usuarios)
            top_bar.addWidget(usuarios_btn)
        
        # Campo de busca
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar solicitações...")
        self.busca_btn = QPushButton("Buscar")
        self.busca_btn.clicked.connect(self.buscar_solicitacoes)
        
        # Botão de atualizar (ADICIONE ESTE CÓDIGO)
        self.atualizar_btn = QPushButton("Atualizar Dados")
        self.atualizar_btn.clicked.connect(self.atualizar_dados)
        top_bar.addWidget(self.atualizar_btn)

        top_bar.addStretch()
        top_bar.addWidget(QLabel("Buscar:"))
        top_bar.addWidget(self.busca_input)
        top_bar.addWidget(self.busca_btn)
        
        layout.addLayout(top_bar)
        
        # Abas
        self.tabs = QTabWidget()
        
        # Importações são feitas aqui para evitar importações circulares
        from .recepcao_window import TelaRecepcao
        from .manutencao_window import TelaManutencao
        from .logs_widget import TelaLogs
        
        # Tela de Recepção
        self.tab_recepcao = TelaRecepcao(self.db, self.usuario_id)
        self.tabs.addTab(self.tab_recepcao, "Recepção")
        
        # Tela de Manutenção
        self.tab_manutencao = TelaManutencao(self.db, self.usuario_id)
        self.tabs.addTab(self.tab_manutencao, "Manutenção")
        
        # Tela de Logs
        self.tab_logs = TelaLogs(self.db)
        self.tabs.addTab(self.tab_logs, "Logs e Usuários Online")
        
        layout.addWidget(self.tabs)
        
        # Informações na barra de status
        self.statusBar().showMessage(f"Conectado como {self.nome_usuario} | Cargo: {self.cargo}")
    
    def abrir_gerenciar_usuarios(self):
        """Abre a janela de gerenciamento de usuários."""
        if self.cargo == "Administrador":
            # Importação dentro da função para evitar importação circular
            from .usuarios_window import GerenciadorUsuarios
            
            dialog = GerenciadorUsuarios(self.db, self.usuario_id)
            dialog.exec_()
            # Atualizar a aba de logs após fechar a janela
            self.tab_logs.atualizar_dados()
    
    def buscar_solicitacoes(self):
        """Busca solicitações com base no termo digitado."""
        termo = self.busca_input.text()
        if not termo:
            QMessageBox.information(self, "Atenção", "Digite um termo para buscar")
            return
        
        # Atualizar ambas as abas com o resultado da busca
        aba_atual = self.tabs.currentIndex()
        
        self.tab_recepcao.atualizar_tabela_com_busca(termo)
        self.tab_manutencao.atualizar_tabela_com_busca(termo)
        
        # Manter na mesma aba
        self.tabs.setCurrentIndex(aba_atual)
    
    def atualizar_dados(self):
        """Atualiza as tabelas de solicitações em todas as abas."""
        # Atualizar a tabela da tela de recepção
        self.tab_recepcao.atualizar_tabela()
        
        # Atualizar a tabela da tela de manutenção
        self.tab_manutencao.atualizar_tabela()
        
        # Atualizar logs e usuários online
        self.tab_logs.atualizar_dados()
        
        # Informar ao usuário
        self.statusBar().showMessage("Dados atualizados com sucesso!", 3000)
    
    def logout(self):
        """Realiza o logout do usuário atual."""
        self.db.registrar_logout(self.usuario_id)
        self.close()
        
        # Import aqui para evitar importação circular
        from .login_window import LoginWindow
        
        login_window = LoginWindow(self.db)
        login_window.show()
    
    def closeEvent(self, event):
        """Trata o evento de fechamento da janela."""
        self.db.registrar_logout(self.usuario_id)
        super().closeEvent(event)