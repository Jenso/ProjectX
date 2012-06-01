# Create your views here.
# from django.http import HttpResponse
# from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, CreateView
from accounts.models import UserProfile, Picture
from index.models import BetaEmail

from django.core.urlresolvers import reverse


class InspirationPageView(ListView):
    """
    """
    context_object_name = "pictures"
    template_name = "index.html"
    queryset = Picture.objects.order_by('-upload_date')
    paginate_by = 30

    def get_context_data(self, **kwargs):   
        context = super(InspirationPageView, self).get_context_data(**kwargs)
        return context
    
    template_name = "inspiration.html"

    
class BetaEmailView(CreateView):
    """
    Display beta page
    """
    template_name = "betaemailpage.html"
    model = BetaEmail

    def __init__(self, *args, **kwargs):
        super(BetaEmailView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        
        self.success_url=reverse('beta_index_page')


class IndexPageView(ListView):
    """
    Display about us page
    """
    context_object_name = "profiles"
    template_name = "index.html"
    queryset = UserProfile.objects.all()

    def get_context_data(self, **kwargs):   
        context = super(IndexPageView, self).get_context_data(**kwargs)
        return context
        

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')
