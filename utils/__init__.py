"""
Pacote de utilitários para o Sistema de Manutenção.
Contém funções auxiliares e ferramentas de uso geral.
"""

from .helpers import validar_email, colorir_tabela_por_status, colorir_tabela_por_prioridade

__all__ = ['validar_email', 'colorir_tabela_por_status', 'colorir_tabela_por_prioridade']