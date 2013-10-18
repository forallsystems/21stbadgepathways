from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as django_auth_views
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from users.models import *
from organizations.models import *
from badges.models import *
from forms import *

def custom_login(request,
                 template_name='login.html',
                 redirect_field_name=REDIRECT_FIELD_NAME,
                 authentication_form=CustomAuthenticationForm):
    
    if request.user.is_authenticated():
       return HttpResponseRedirect("/dashboard/")
    
    """Displays the login form and handles the login action."""
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            django_auth_views.auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    #current_site = get_current_site(request)
  
    pathway_list = Pathway.get_pathway_list()

    return render_to_response(template_name, {
        'form': form,
        'pathway_list':pathway_list,
        redirect_field_name: redirect_to,
        #'site': current_site,
        #'site_name': current_site.name,
    }, context_instance=RequestContext(request))
    


@login_required
def init_login(request):
    #Determine user's role
    request.session['USER_ROLE'] = request.user.get_profile().get_role()
    org = Organization.get_user_organization(request.user.id)
    request.session['USER_ORGANIZATION_ID'] = org.id
    request.session['USER_ORGANIZATION_TYPE'] = org.type
    request.session['USER_ORGANIZATION_NAME'] = org.name
    request.session['USER_NAME'] = request.user.get_full_name()
    #Determine user's root organization
    
    return HttpResponseRedirect("/dashboard/")
    
@login_required
def dashboard(request, templateName='studentDashboard.html'):
    try:
        user_role = request.session['USER_ROLE']
        if user_role in (Role.DISTRICTADMIN, Role.SCHOOLADMIN):
            return render(request,'adminDashboard.html',{'first_name':request.user.first_name,'last_name':request.user.last_name})
        elif user_role == Role.STUDENT: 
            num_awards = Award.get_user_num_awards(request.user.id)
            points_balance = PointsBalance.get_user_points_balance(request.user.id)
            pathway_list = Pathway.get_user_pathway_list(request.user.id)
            
            #determine student's age
            allow_backpack = 0
            sp = request.user.get_profile().get_student_profile()
            if sp.get_age() >= 13 and request.user.email!='':
                allow_backpack = 1
            
            return render(request,templateName,{'first_name':request.user.first_name,
                                                                       'last_name':request.user.last_name,
                                                                       'num_awards':num_awards,
                                                                       'allow_backpack':allow_backpack,
                                                                       'points_balance':points_balance,
                                                                       'pathway_list':pathway_list,
                                                                       'base_url':request.get_host()})
    except:
        import sys
        print sys.exc_info()
        pass
    return render(request,'error.html')

@login_required
def dashboard_browse_passport(request):
    return dashboard(request,templateName='studentDashboardBrowse.html')

    