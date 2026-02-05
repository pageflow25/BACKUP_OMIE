"""
Middleware para seleção de banco de dados.
Captura o banco selecionado da sessão e configura para o router.
"""
from django.conf import settings
from .routers import set_current_database


class COOPDisableMiddleware:
    """
    Middleware que desabilita o Cross-Origin-Opener-Policy header para
    acesso via HTTP ou endereços IP em desenvolvimento.
    Remove o header COOP que causa avisos no navegador para origens não-seguras.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Remover COOP header em desenvolvimento/HTTP
        if settings.DEBUG or request.scheme == 'http':
            if 'Cross-Origin-Opener-Policy' in response:
                del response['Cross-Origin-Opener-Policy']
        
        return response


class DatabaseSelectorMiddleware:
    """
    Middleware que lê o banco de dados selecionado da sessão
    e configura para uso no router.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Obter banco da sessão ou usar padrão
        db_alias = request.session.get('selected_database', 'cdg')
        
        # Validar se o banco existe
        available_dbs = list(settings.DATABASE_NAMES.keys())
        if db_alias not in available_dbs:
            db_alias = 'cdg'
        
        # Configurar o banco para esta requisição
        set_current_database(db_alias)
        
        # Adicionar informação ao request para uso nos templates
        request.current_database = db_alias
        request.current_database_name = settings.DATABASE_NAMES.get(db_alias, db_alias)
        request.available_databases = settings.DATABASE_NAMES
        
        response = self.get_response(request)
        return response
