"""
Database Router para suporte a múltiplos bancos de dados.
Permite selecionar qual banco utilizar baseado na sessão do usuário.
"""
import threading

# Thread-local storage para armazenar o banco atual
_thread_locals = threading.local()


def set_current_database(db_alias):
    """Define o banco de dados atual para a thread"""
    _thread_locals.current_db = db_alias


def get_current_database():
    """Retorna o banco de dados atual da thread"""
    return getattr(_thread_locals, 'current_db', 'cdg')  # CDG como padrão


class MultiDatabaseRouter:
    """
    Router que direciona queries para o banco de dados selecionado.
    - Modelos do app 'core' usam o banco selecionado na sessão
    - Modelos do Django (auth, sessions, etc) usam o banco 'default'
    """
    
    # Models do Django que devem sempre usar o banco default
    DJANGO_APPS = {'auth', 'contenttypes', 'sessions', 'admin', 'messages'}
    
    def db_for_read(self, model, **hints):
        """Retorna o banco para leitura"""
        if model._meta.app_label in self.DJANGO_APPS:
            return 'default'
        if model._meta.app_label == 'core':
            return get_current_database()
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Retorna o banco para escrita"""
        if model._meta.app_label in self.DJANGO_APPS:
            return 'default'
        if model._meta.app_label == 'core':
            return get_current_database()
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Permite relações entre objetos do mesmo banco"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Controla onde as migrações podem ser executadas.
        - Apps do Django só migram no 'default'
        - App 'core' não precisa de migrações (managed=False)
        """
        if app_label in self.DJANGO_APPS:
            return db == 'default'
        return None
