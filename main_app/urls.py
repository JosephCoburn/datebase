from django.urls import path, include
from . import views

urlpatterns = [
    # PROFILE & ACCOUNT
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', views.signup, name="signup"),
    path('profile/<int:pk>', views.user_detail, name="profile"),
    path('profile/create', views.ProfileCreate.as_view(), name="profile_create"),
    path('profile/<int:pk>/update/', views.ProfileUpdate.as_view(), name="profile_update"),
    path('profile/<int:pk>/delete/', views.ProfileDelete.as_view(), name="profile_delete"),
    # MATCHES
    path('matches/', views.matches_index, name='matches_index'),
    path('matches/create', views.MatchCreate.as_view(), name="matches_create"),
    path('matches/<int:pk>/', views.match_detail, name="match_detail"),
    path('matches/<int:pk>/update/', views.MatchUpdate.as_view(), name="match_update"),
    path('matches/<int:pk>/add_note/', views.add_note, name='add_note'),
    path('matches/<int:pk>/delete_note/<int:note_id>', views.delete_note, name="delete_note"),
    path('matches/<int:pk>/delete/', views.MatchDelete.as_view(), name="match_delete"),
    # RDVS
    path('rdvs/', views.RdvList.as_view(), name='rdvs_index'),
    path('rdvs/create', views.RdvCreate.as_view(), name="rdvs_create"),
    path('rdvs/<int:pk>', views.RdvDetail.as_view(), name="rdv_detail"),
    path('rdvs/<int:pk>/update/', views.RdvUpdate.as_view(), name="rdv_update"),
    path('rdvs/<int:pk>/delete/', views.RdvDelete.as_view(), name="rdv_delete"),

    path('matches/<int:match_id>/add_match_photo/', views.add_match_photo, name="add_match_photo"),
    path('profile/<int:profile_id>/add_profile_photo/', views.add_profile_photo, name="add_profile_photo"),
    # Add calendar link
    path('calendar/<int:pk>/', views.cal, name='add_calendar'),
    #  Ghost
    path('ghost/<int:pk>/', views.ghost, name='match_ghost'),
    # Add Yelp link
    path('yelp/<int:pk>/', views.yelp, name='yelp_search'),
]