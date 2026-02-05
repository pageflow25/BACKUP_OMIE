from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings


@require_POST
@staff_member_required
def select_database(request):
    """View para selecionar o banco de dados via sessão"""
    db_alias = request.POST.get('database', 'cdg')
    
    # Validar se o banco existe
    available_dbs = list(settings.DATABASE_NAMES.keys())
    if db_alias in available_dbs:
        request.session['selected_database'] = db_alias
    
    # Redirecionar de volta para a página anterior ou admin
    referer = request.META.get('HTTP_REFERER', '/admin/')
    return redirect(referer)
