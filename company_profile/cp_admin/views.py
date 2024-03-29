from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.template.loader import render_to_string
from dispatcher.views import Dispatcher
from .forms import CmsLoginForm

import time
from company_profile.cp_user_configs.models import UserConfigs
from company_profile.cp_articles.views import CPArticle
from company_profile.cp_pages.views import CPPage

class Logout(Dispatcher):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('cms:login'))
    def post(self, request, *args, **kwargs):
        pass

class Login(Dispatcher):
    template = "cp_admin/index.html"
    form = CmsLoginForm()
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code', 200)
        token = get_token(request)
        data = super(Login, self).get(request, args, kwargs)
        configs = UserConfigs.objects.get(member = data['member'])
        self.component['base']='cp_admin/component/login_base.html'
        self.component['header']='cp_admin/component/login_header.html'
        self.component['main']='cp_admin/component/login_main.html'
        self.component['local_script']='cp_admin/component/login_local_script.html'
        return render(request, self.template, {
                'component': self.component,
                'form' : self.form,
                'token' : token,
                'code' : code
            }
        )
    def post(self, request, *args, **kwargs):
        token = get_token(request)
        self.form = CmsLoginForm(request.POST)
        if self.form.is_valid():
            data = super(Login, self).get(request, args, kwargs)
            post_data = self.form.cleaned_data
            username = post_data.get('username')
            password = post_data.get('password')
            if request.user.is_authenticated:
                logout(request)
            user = authenticate(username=username,
                password=password)
            if user is not None : 
                if user.user_member.site == data['site']:
                    login(request, user)
                    return JsonResponse({'new_token': get_token(request), 'redirect_url':reverse('cms:index')}, status=200)
                else:
                    return  HttpResponse(status=403)
            return HttpResponse(status=404)

class Index(LoginRequiredMixin, Dispatcher):
    login_url = '/cms/login/'
    template = "cp_admin/index.html"
    component = {}
    component['base']='cp_admin/component/index_base.html'
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        data = super(Index, self).get(request, args, kwargs)
        member = data['member']
        configs = UserConfigs.objects.get(member = member)
        site = data['site']
        self.component['header'] =  'cp_admin/component/index_header.html'
        self.component['main'] = 'cp_admin/component/index_main.html'
        self.component['local_script'] = 'cp_admin/component/index_local_script.html'

        if(request.GET.get('method', '') == 'get_component'):
            return self.get_component(request, token, data, configs, site, member)

        return render(request, self.template, {
                'member': member,
                'data': data,
                'configs': configs,
                'site': site,
                'token': token,
                'component':self.component
            }
        )
    def post(self, request, *args, **kwargs):
        pass
    def get_component(self, request, token, data, configs, site, member):
        header =  render_to_string(self.component['header'], 
                                    {'token': token, 'member': member,'data': data, 'site': site, 'configs': configs})
        main = render_to_string(self.component['main'], 
                                    {'token': token, 'member': member,'data': data, 'site': site, 'configs': configs})
        local_script = render_to_string(self.component['local_script'], 
                                    {'token': token, 'member': member,'data': data, 'site': site, 'configs': configs})

        return JsonResponse({'main': main,
                            'local_script': local_script,
                            'header': header}, status=200)

class CmsArticle(CPArticle):
    def get(self, request, *args, **kwargs):
        try:
            action = kwargs['action']
        except:
            action = 'show_all'
        
        try:
            pk = kwargs['pk']
        except:
            pk = 'none'

        return super(CmsArticle, self).get(request, args, action=action, pk=pk)


class CmsPage(CPPage):
    def get(self, request, *args, **kwargs):
        try:
            action = kwargs['action']
        except:
            action = 'show_all'
        
        try:
            pk = kwargs['pk']
        except:
            pk = 'none'

        return super(CmsPage, self).get(request, args, action=action, pk=pk)


