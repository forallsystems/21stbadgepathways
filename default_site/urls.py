from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('', 
     url(r'^admin/', include(admin.site.urls)),
     
     (r'^password_change/$', 'django.contrib.auth.views.password_change'),
     (r'^password_change/done/$', 'django.contrib.auth.views.password_change_done'),
     (r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
     (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
     (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
     (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    
     (r'^$', 'default_site.views.custom_login', {'template_name': 'login.html'}),
     
     (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
     
     (r'^init_login/$', 'default_site.views.init_login'),
     (r'^dashboard/$', 'default_site.views.dashboard'),
     (r'^dashboard/browse/$', 'default_site.views.dashboard_browse_passport'),
     
     (r'^my_account/$', 'users.views.edit_myaccount'),
     
     (r'^awards/assertion/(?P<award_id>(\w|\-)+)/$', 'badges.views.obi_assertion'),
     
     (r'^redeem/$', 'store.views.redeem'),
     (r'^redeem/add/(?P<item_id>(\w|\-)+)/$', 'store.views.add_to_cart'),
     (r'^redeem/remove/(?P<item_id>(\w|\-)+)/$', 'store.views.remove_from_cart'),
     (r'^redeem/complete/$', 'store.views.complete_order'),
     (r'^redeem/history/$', 'store.views.order_history'),
     
     (r'^my_badges/$','badges.views.my_badges'),
     (r'^my_pathways/$','badges.views.my_pathways'),
     (r'^my_pathways/update_sort/$','badges.views.update_my_pathways_sort'),
     (r'^my_pathways/add/(?P<pathway_id>(\w|\-)+)/$','badges.views.add_pathway'),
     (r'^my_pathways/delete/(?P<pathway_id>(\w|\-)+)/$','badges.views.delete_pathway'),
     
     (r'^reports/redemptions/$', 'store.views.point_redemptions'),
     (r'^reports/pathways/$', 'badges.views.pathway_summary'),
     (r'^reports/pathways/badges/$', 'badges.views.pathway_badge_completion'),
     (r'^reports/badges/$', 'badges.views.badge_completion'),
     
     (r'^pathways/$', 'badges.views.list_pathways'),
     (r'^pathways/sort/$', 'badges.views.sort_pathways'),
     (r'^pathways/update_sort/$', 'badges.views.update_pathway_sort'),
     (r'^pathways/add/$', 'badges.views.add_pathway'),
     (r'^pathways/edit/(?P<pathway_id>(\w|\-)+)/$', 'badges.views.edit_pathway'),
     (r'^pathways/delete/(?P<pathway_id>(\w|\-)+)/$', 'badges.views.delete_pathway'),
     (r'^pathways/copy/(?P<pathway_id>(\w|\-)+)/$', 'badges.views.copy_pathway'),
     
     (r'^pathways/badges/$', 'badges.views.list_pathway_badges'),
     (r'^pathways/badges/add/(?P<badge_id>(\w|\-)+)/$', 'badges.views.add_pathway_badge'),
     (r'^pathways/badges/delete/(?P<badge_id>(\w|\-)+)/$', 'badges.views.delete_pathway_badge'),
     (r'^pathways/badges/update_sort/$', 'badges.views.update_pathway_badges_sort'),
     
     
     (r'^pathways/details/$', 'badges.ajaxviews.get_pathway_details'),
     (r'^pathways/badges/json/$', 'badges.ajaxviews.get_pathway_badges'),
     (r'^badges/detail/$', 'badges.ajaxviews.get_badge_details'),
     (r'^pathways/awards/json/$', 'badges.ajaxviews.get_pathway_awards'),
     (r'^awards/detail/$', 'badges.ajaxviews.get_award_details'),
     
     
     (r'^badges/$', 'badges.views.list_badges'),
     (r'^badges/add/$', 'badges.views.add_badge'),
     (r'^badges/edit/(?P<badge_id>(\w|\-)+)/$', 'badges.views.edit_badge'),
     (r'^badges/delete/(?P<badge_id>(\w|\-)+)/$', 'badges.views.delete_badge'),
     (r'^badges/copy/(?P<badge_id>(\w|\-)+)/$', 'badges.views.copy_badge'),
     (r'^badges/criteria/(?P<badge_id>(\w|\-)+)/$', 'badges.views.public_badge_details'),
     
     (r'^students/$', 'users.views.list_students'),
    
     (r'^students/add/(?P<school_id>(\w|\-)+)/$', 'users.views.add_student'),
     (r'^students/edit/(?P<studentprofile_id>(\w|\-)+)/$', 'users.views.edit_student'),
     (r'^students/delete/(?P<studentprofile_id>(\w|\-)+)/$', 'users.views.delete_student'),
     
     (r'^students/awards/$', 'badges.views.list_awards'),
     (r'^students/awards/issue/$', 'badges.views.issue_award'),
     (r'^students/awards/delete/(?P<award_id>(\w|\-)+)/$', 'badges.views.delete_award'),
     
     (r'^vendors/$', 'store.views.list_vendors'),
     (r'^vendors/add/$', 'store.views.add_vendor'),
     (r'^vendors/edit/(?P<vendor_id>(\w|\-)+)/$', 'store.views.edit_vendor'),
     (r'^vendors/delete/(?P<vendor_id>(\w|\-)+)/$', 'store.views.delete_vendor'),
     
     (r'^vendors/items/$', 'store.views.list_items'),
     (r'^vendors/items/add/(?P<vendor_id>(\w|\-)+)/$', 'store.views.add_item'),
     (r'^vendors/items/edit/(?P<item_id>(\w|\-)+)/$', 'store.views.edit_item'),
     (r'^vendors/items/delete/(?P<item_id>(\w|\-)+)/$', 'store.views.delete_item'),
     
     (r'^districtadmins/$', 'users.views.list_districtadmins'),
     (r'^districtadmins/add/$', 'users.views.add_districtadmin'),
     (r'^districtadmins/edit/(?P<userprofile_id>(\w|\-)+)/$', 'users.views.edit_districtadmin'),
     (r'^districtadmins/delete/(?P<userprofile_id>(\w|\-)+)/$', 'users.views.delete_districtadmin'),
)
