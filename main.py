#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ponto de entrada principal para o Sistema de Cadastro de Produtos para Manutenção.
Este arquivo inicia a aplicação e configura o ambiente.
"""

import sys
from PyQt5.QtWidgets import QApplication
from database.database import Database
from ui.login_window import LoginWindow

def main():
    """Função principal que inicia o aplicativo."""
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle("Fusion")
    
    # Criar instância do banco de dados
    db = Database()
    
    # Abrir janela de login
    login_window = LoginWindow(db)
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()