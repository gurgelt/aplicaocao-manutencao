#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definição do esquema do banco de dados SQL Server para o Sistema de Manutenção.
Este arquivo contém as instruções SQL para criação das tabelas.
"""

# Script SQL para criar as tabelas do banco de dados SQL Server
SQL_SERVER_SCRIPT = """
-- Tabela de usuários
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios')
BEGIN
    CREATE TABLE usuarios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(255) NOT NULL,
        usuario NVARCHAR(255) UNIQUE NOT NULL,
        senha NVARCHAR(255) NOT NULL,
        cargo NVARCHAR(255) NOT NULL,
        ativo BIT DEFAULT 1
    );
END
GO

-- Tabela de solicitacoes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'solicitacoes')
BEGIN
    CREATE TABLE solicitacoes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        ordem_servico NVARCHAR(255) UNIQUE NOT NULL,
        nome_responsavel NVARCHAR(255) NOT NULL,
        nome_empresa NVARCHAR(255) NOT NULL,
        telefone NVARCHAR(255) NOT NULL,
        email NVARCHAR(255) NOT NULL,
        local_recebimento NVARCHAR(255) NOT NULL,
        historico_cliente NVARCHAR(MAX) NOT NULL,
        descricao_problema NVARCHAR(MAX) NOT NULL,
        marca_motor NVARCHAR(255) NOT NULL,
        modelo_motor NVARCHAR(255) NOT NULL,
        condicao_peca NVARCHAR(255) NOT NULL,
        data_criacao NVARCHAR(255) NOT NULL,
        codigo_motor NVARCHAR(255),
        prioridade NVARCHAR(255) DEFAULT 'Normal',
        status NVARCHAR(255) DEFAULT 'Pendente',
        diagnostico NVARCHAR(MAX)
    );
END
GO

-- Tabela de imagens
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'imagens')
BEGIN
    CREATE TABLE imagens (
        id INT IDENTITY(1,1) PRIMARY KEY,
        solicitacao_id INT NOT NULL,
        imagem VARBINARY(MAX) NOT NULL,
        FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id)
    );
END
GO

-- Tabela de logs
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'logs')
BEGIN
    CREATE TABLE logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        acao NVARCHAR(255) NOT NULL,
        descricao NVARCHAR(255) NOT NULL,
        data_hora NVARCHAR(255) NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
END
GO

-- Tabela de usuarios_online
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios_online')
BEGIN
    CREATE TABLE usuarios_online (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
END
GO
"""