#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementação da classe Database para o Sistema de Manutenção.
Esta classe gerencia todas as operações de acesso ao banco de dados SQL Server.
"""

import pyodbc
import hashlib
from datetime import datetime

from .schema import SQL_SERVER_SCRIPT

class Database:
    """Classe para gerenciar operações no banco de dados SQL Server."""
    
    def __init__(self):
        """Inicializa a conexão com o banco de dados."""
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Inicializa o banco de dados e cria as tabelas, se necessário."""
        try:
            # Configuração de conexão com SQL Server
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=localhost\\SQLEXPRESS01;'
                'DATABASE=manutencao;'
                'Trusted_Connection=yes;'
                'TrustServerCertificate=yes;'
            )
            
            
            cursor = self.conn.cursor()
            
            # Verificar se as tabelas já existem
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios'")
            if cursor.fetchone()[0] == 0:
                # Executar script de criação das tabelas
                for command in SQL_SERVER_SCRIPT.split('GO'):
                    if command.strip():
                        cursor.execute(command)
                
                # Criar usuário admin padrão
                senha_hash = self.hash_password("admin")
                cursor.execute(
                    "INSERT INTO usuarios (nome, usuario, senha, cargo, ativo) VALUES (?, ?, ?, ?, ?)",
                    ("Administrador", "admin", senha_hash, "Administrador", 1)
                )
            else:
                # Verificar se já existe um usuário admin
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = 'admin'")
                if cursor.fetchone()[0] == 0:
                    # Criar usuário admin padrão
                    senha_hash = self.hash_password("admin")
                    cursor.execute(
                        "INSERT INTO usuarios (nome, usuario, senha, cargo, ativo) VALUES (?, ?, ?, ?, ?)",
                        ("Administrador", "admin", senha_hash, "Administrador", 1)
                    )
            
            self.conn.commit()
        except pyodbc.Error as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            if self.conn:
                self.conn.close()
    
    def hash_password(self, senha):
        """Gera um hash da senha usando SHA-256."""
        senha_bytes = senha.encode('utf-8')
        hash_obj = hashlib.sha256(senha_bytes)
        return hash_obj.hexdigest()
    
    def verificar_senha(self, senha_digitada, senha_hash):
        """Verifica se a senha digitada corresponde ao hash armazenado."""
        return self.hash_password(senha_digitada) == senha_hash
    
    def autenticar_usuario(self, usuario, senha):
        """Autentica um usuário com nome de usuário e senha."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, nome, senha, cargo, ativo FROM usuarios WHERE usuario = ?", (usuario,))
            usuario_encontrado = cursor.fetchone()
            
            if usuario_encontrado and usuario_encontrado[4] == 1:  # Verifica se está ativo
                id_usuario, nome, senha_hash, cargo, _ = usuario_encontrado
                if self.verificar_senha(senha, senha_hash):
                    # Registra usuário como online
                    cursor.execute("INSERT INTO usuarios_online (usuario_id) VALUES (?)", (id_usuario,))
                    self.conn.commit()
                    return id_usuario, nome, cargo
            return None
        except pyodbc.Error as e:
            print(f"Erro ao autenticar: {e}")
            return None
    
    def registrar_logout(self, usuario_id):
        """Registra o logout de um usuário removendo-o da tabela de usuários online."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM usuarios_online WHERE usuario_id = ?", (usuario_id,))
            self.conn.commit()
        except pyodbc.Error as e:
            print(f"Erro ao registrar logout: {e}")
    
    def registrar_log(self, usuario_id, acao, descricao):
        """Registra uma ação no log do sistema."""
        try:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO logs (usuario_id, acao, descricao, data_hora) VALUES (?, ?, ?, ?)",
                (usuario_id, acao, descricao, agora)
            )
            self.conn.commit()
        except pyodbc.Error as e:
            print(f"Erro ao registrar log: {e}")
    
    def obter_usuarios(self):
        """Obtém a lista de todos os usuários cadastrados."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, nome, usuario, cargo, ativo FROM usuarios")
            return cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Erro ao obter usuários: {e}")
            return []
    
    def obter_usuarios_online(self):
        """Obtém a lista de usuários atualmente online."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT u.nome, u.usuario FROM usuarios_online uo
                JOIN usuarios u ON uo.usuario_id = u.id
            """)
            return cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Erro ao obter usuários online: {e}")
            return []
    
    def obter_logs(self, limite=50):
        """Obtém os registros de log mais recentes."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT TOP(?) u.nome, l.acao, l.descricao, l.data_hora FROM logs l
                JOIN usuarios u ON l.usuario_id = u.id
                ORDER BY l.data_hora DESC
            """, (limite,))
            return cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Erro ao obter logs: {e}")
            return []
    
    def adicionar_usuario(self, nome, usuario, senha, cargo):
        """Adiciona um novo usuário ao sistema."""
        try:
            cursor = self.conn.cursor()
            # Verificar se já existem 2 administradores
            if cargo == "Administrador":
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cargo = 'Administrador' AND ativo = 1")
                if cursor.fetchone()[0] >= 2:
                    return False, "Já existem 2 administradores cadastrados"
            
            senha_hash = self.hash_password(senha)
            cursor.execute(
                "INSERT INTO usuarios (nome, usuario, senha, cargo, ativo) VALUES (?, ?, ?, ?, ?)",
                (nome, usuario, senha_hash, cargo, 1)
            )
            self.conn.commit()
            return True, "Usuário cadastrado com sucesso"
        except pyodbc.IntegrityError:
            return False, "Nome de usuário já existe"
        except pyodbc.Error as e:
            return False, f"Erro ao adicionar usuário: {e}"
    
    def atualizar_usuario(self, id_usuario, nome, usuario, senha, cargo):
        """Atualiza os dados de um usuário existente."""
        try:
            cursor = self.conn.cursor()
            
            # Verificar se já existem 2 administradores se estiver alterando para admin
            if cargo == "Administrador":
                cursor.execute("""
                    SELECT COUNT(*) FROM usuarios 
                    WHERE cargo = 'Administrador' AND ativo = 1 AND id != ?
                """, (id_usuario,))
                
                # Verificar se o usuário já é admin
                cursor.execute("SELECT cargo FROM usuarios WHERE id = ?", (id_usuario,))
                cargo_atual = cursor.fetchone()[0]
                
                # Corrigindo o erro de lógica aqui - não chamamos fetchone() duas vezes
                admins_count = cursor.execute("""
                    SELECT COUNT(*) FROM usuarios 
                    WHERE cargo = 'Administrador' AND ativo = 1 AND id != ?
                """, (id_usuario,)).fetchone()[0]
                
                if cargo_atual != "Administrador" and admins_count >= 2:
                    return False, "Já existem 2 administradores cadastrados"
            
            if senha:  # Se a senha foi fornecida, atualiza
                senha_hash = self.hash_password(senha)
                cursor.execute(
                    "UPDATE usuarios SET nome = ?, usuario = ?, senha = ?, cargo = ? WHERE id = ?",
                    (nome, usuario, senha_hash, cargo, id_usuario)
                )
            else:  # Caso contrário, mantém a senha atual
                cursor.execute(
                    "UPDATE usuarios SET nome = ?, usuario = ?, cargo = ? WHERE id = ?",
                    (nome, usuario, cargo, id_usuario)
                )
            
            self.conn.commit()
            return True, "Usuário atualizado com sucesso"
        except pyodbc.IntegrityError:
            return False, "Nome de usuário já existe"
        except pyodbc.Error as e:
            return False, f"Erro ao atualizar usuário: {e}"
    
    def desativar_usuario(self, id_usuario):
        """Desativa um usuário (não exclui do banco)."""
        try:
            cursor = self.conn.cursor()
            
            # Verificar se é o último administrador
            cursor.execute("SELECT cargo FROM usuarios WHERE id = ?", (id_usuario,))
            cargo = cursor.fetchone()[0]
            
            if cargo == "Administrador":
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cargo = 'Administrador' AND ativo = 1")
                if cursor.fetchone()[0] <= 1:
                    return False, "Não é possível desativar o último administrador"
            
            cursor.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (id_usuario,))
            self.conn.commit()
            return True, "Usuário desativado com sucesso"
        except pyodbc.Error as e:
            return False, f"Erro ao desativar usuário: {e}"
    
    def obter_solicitacoes(self):
        """Obtém todas as solicitações cadastradas."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, ordem_servico, nome_responsavel, nome_empresa, telefone, 
                email, local_recebimento, historico_cliente, descricao_problema, 
                marca_motor, modelo_motor, condicao_peca, data_criacao, 
                codigo_motor, prioridade, status, diagnostico 
                FROM solicitacoes
                ORDER BY id DESC
            """)
            return cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Erro ao obter solicitações: {e}")
            return []
    
    def obter_solicitacao_por_id(self, solicitacao_id):
        """Obtém uma solicitação específica pelo ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, ordem_servico, nome_responsavel, nome_empresa, telefone, 
                email, local_recebimento, historico_cliente, descricao_problema, 
                marca_motor, modelo_motor, condicao_peca, data_criacao, 
                codigo_motor, prioridade, status, diagnostico 
                FROM solicitacoes WHERE id = ?
            """, (solicitacao_id,))
            return cursor.fetchone()
        except pyodbc.Error as e:
            print(f"Erro ao obter solicitação: {e}")
            return None
    
    def gerar_ordem_servico(self):
        """Gera um número de ordem de serviço no formato mmAA-n."""
        try:
            # Formato mmAA-n
            hoje = datetime.now()
            mes_ano = hoje.strftime("%m%y")
            
            cursor = self.conn.cursor()
            # Verificar última OS do mês atual
            cursor.execute(
                "SELECT ordem_servico FROM solicitacoes WHERE ordem_servico LIKE ? ORDER BY id DESC", 
                (f"{mes_ano}-%",)
            )
            
            ultima_os = cursor.fetchone()
            if ultima_os:
                # Extrair o número após o traço e incrementar
                numero = int(ultima_os[0].split('-')[1]) + 1
            else:
                numero = 1
                
            nova_os = f"{mes_ano}-{numero}"
            return nova_os
        except pyodbc.Error as e:
            print(f"Erro ao gerar ordem de serviço: {e}")
            return None
    
    def adicionar_solicitacao(self, dados, usuario_id):
        """Adiciona uma nova solicitação ao sistema."""
        try:
            cursor = self.conn.cursor()
            
            # Gerar OS
            ordem_servico = self.gerar_ordem_servico()
            
            cursor.execute("""
                INSERT INTO solicitacoes (
                    ordem_servico, nome_responsavel, nome_empresa, telefone, email, 
                    local_recebimento, historico_cliente, descricao_problema, 
                    marca_motor, modelo_motor, condicao_peca, data_criacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ordem_servico, dados['nome_responsavel'], dados['nome_empresa'],
                dados['telefone'], dados['email'], dados['local_recebimento'],
                dados['historico_cliente'], dados['descricao_problema'],
                dados['marca_motor'], dados['modelo_motor'], dados['condicao_peca'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # Obter o ID da solicitação recém-inserida - adaptado para SQL Server
            cursor.execute("SELECT @@IDENTITY")
            solicitacao_id = cursor.fetchone()[0]
            
            # Registrar log
            self.registrar_log(
                usuario_id, 
                "Criação", 
                f"Criou solicitação {solicitacao_id} (OS: {ordem_servico})"
            )
            
            self.conn.commit()
            return True, solicitacao_id, ordem_servico
        except pyodbc.Error as e:
            print(f"Erro ao adicionar solicitação: {e}")
            return False, None, None
    
    def atualizar_solicitacao(self, solicitacao_id, dados, usuario_id):
        """Atualiza uma solicitação existente."""
        try:
            cursor = self.conn.cursor()
            
            # Verificar status e diagnóstico para validação
            if dados.get('status') == 'Concluído' and not dados.get('diagnostico'):
                return False, "É necessário incluir um diagnóstico para concluir"
            
            # Atualizar campos da recepção e manutenção
            cursor.execute("""
                UPDATE solicitacoes SET 
                nome_responsavel = ?, nome_empresa = ?, telefone = ?, email = ?, 
                local_recebimento = ?, historico_cliente = ?, descricao_problema = ?, 
                marca_motor = ?, modelo_motor = ?, condicao_peca = ?, 
                codigo_motor = ?, prioridade = ?, status = ?, diagnostico = ?
                WHERE id = ?
            """, (
                dados['nome_responsavel'], dados['nome_empresa'], dados['telefone'], dados['email'],
                dados['local_recebimento'], dados['historico_cliente'], dados['descricao_problema'],
                dados['marca_motor'], dados['modelo_motor'], dados['condicao_peca'],
                dados.get('codigo_motor'), dados.get('prioridade', 'Normal'), 
                dados.get('status', 'Pendente'), dados.get('diagnostico'),
                solicitacao_id
            ))
            
            # Registrar log
            self.registrar_log(
                usuario_id, 
                "Atualização", 
                f"Atualizou solicitação {solicitacao_id}"
            )
            
            self.conn.commit()
            return True, "Solicitação atualizada com sucesso"
        except pyodbc.Error as e:
            print(f"Erro ao atualizar solicitação: {e}")
            return False, f"Erro ao atualizar: {e}"
    
    def excluir_solicitacao(self, solicitacao_id, usuario_id):
        """Exclui uma solicitação e suas imagens associadas."""
        try:
            cursor = self.conn.cursor()
            
            # Buscar ordem de serviço para log
            cursor.execute("SELECT ordem_servico FROM solicitacoes WHERE id = ?", (solicitacao_id,))
            ordem_servico = cursor.fetchone()[0]
            
            # Excluir imagens primeiro
            cursor.execute("DELETE FROM imagens WHERE solicitacao_id = ?", (solicitacao_id,))
            
            # Excluir solicitação
            cursor.execute("DELETE FROM solicitacoes WHERE id = ?", (solicitacao_id,))
            
            # Registrar log
            self.registrar_log(
                usuario_id, 
                "Exclusão", 
                f"Excluiu solicitação {solicitacao_id} (OS: {ordem_servico})"
            )
            
            self.conn.commit()
            return True, "Solicitação excluída com sucesso"
        except pyodbc.Error as e:
            print(f"Erro ao excluir solicitação: {e}")
            return False, f"Erro ao excluir: {e}"
    
    def salvar_imagem(self, solicitacao_id, imagem_bytes):
        """Salva uma imagem associada a uma solicitação."""
        try:
            cursor = self.conn.cursor()
            
            # Verificar quantidade de imagens
            cursor.execute("SELECT COUNT(*) FROM imagens WHERE solicitacao_id = ?", (solicitacao_id,))
            if cursor.fetchone()[0] >= 10:
                return False, "Limite de 10 imagens atingido"
            
            cursor.execute("INSERT INTO imagens (solicitacao_id, imagem) VALUES (?, ?)", 
                           (solicitacao_id, pyodbc.Binary(imagem_bytes)))
            
            self.conn.commit()
            return True, "Imagem salva com sucesso"
        except pyodbc.Error as e:
            print(f"Erro ao salvar imagem: {e}")
            return False, f"Erro ao salvar imagem: {e}"
    
    def obter_imagens(self, solicitacao_id):
        """Obtém todas as imagens associadas a uma solicitação."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, imagem FROM imagens WHERE solicitacao_id = ?", (solicitacao_id,))
            return cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Erro ao obter imagens: {e}")
            return []
    
    def excluir_imagem(self, imagem_id):
        """Exclui uma imagem específica pelo ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM imagens WHERE id = ?", (imagem_id,))
            self.conn.commit()
            return True, "Imagem excluída com sucesso"
        except pyodbc.Error as e:
            print(f"Erro ao excluir imagem: {e}")
            return False, f"Erro ao excluir imagem: {e}"
    
    def buscar_solicitacoes(self, termo):
        """Busca solicitações que correspondam a um termo de pesquisa."""
        try:
            cursor = self.conn.cursor()
            termo_busca = f"%{termo}%"
            cursor.execute("""
                SELECT id, ordem_servico, nome_responsavel, nome_empresa, telefone, 
                email, local_recebimento, historico_cliente, descricao_problema, 
                marca_motor, modelo_motor, condicao_peca, data_criacao, 
                codigo_motor, prioridade, status, diagnostico 
                FROM solicitacoes
                WHERE 
                    ordem_servico LIKE ? OR 
                    nome_responsavel LIKE ? OR 
                    nome_empresa LIKE ? OR 
                    modelo_motor LIKE ? OR
                    descricao_problema LIKE ? OR
                    status LIKE ?
                ORDER BY id DESC
            """, (termo_busca, termo_busca, termo_busca, termo_busca, termo_busca, termo_busca))
            return cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Erro ao buscar solicitações: {e}")
            return []