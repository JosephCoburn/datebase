from __future__ import print_function
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.db import models
from .models import Match, Rdv, Match_photo, User_photo, Profile, Match_notes
from .forms import RdvForm, NotesForm
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid
import boto3
# Cal API imports
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from django.utils import timezone
# Yelp API
import requests
import json

S3_BASE_URL = 'https://s3-us-west-1.amazonaws.com/'
BUCKET = 'datebase'

# Create your views here.
def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('matches_index')
    else:
      error_message = 'Invalid Credentials - Try Again'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

@login_required
def add_match_photo(request, match_id):
  print(match_id)
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      photo = Match_photo(url=url, match_id=match_id)
      photo.save()
    except:
      print('An error occurred uploading file to S3')
  return redirect('match_detail', pk=match_id)

@login_required
def add_profile_photo(request, profile_id):
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f"{S3_BASE_URL}{BUCKET}/{key}"
      photo = User_photo(url=url, user_id=profile_id)
      photo.save()
    except:
      print('An error occurred uploading file to S3')
  return redirect('profile', pk=profile_id)


def home(request):
    return render(request, 'home.html')


def about(request):
  return render(request, 'about.html')

@login_required
def matches_index(request):
  matches = Match.objects.filter(user=request.user)
  return render(request, 'matches/index.html', {'matches': matches})

class MatchCreate(LoginRequiredMixin, CreateView):
  model = Match
  fields = ['name', 'email', 'phone_number', 'age', 'location', 'meet', 'interests', 'zodiac']
  success_url = '/matches/'

  def form_valid(self, form):
  # Assign the logged in user
    form.instance.user = self.request.user
    # Let the CreateView do its job as usual
    return super().form_valid(form)

@login_required
def match_detail(request, pk):
  match = Match.objects.get(id=pk)
  print(match.ghost)
  notes_form = NotesForm()
  return render(request, 'matches/match_detail.html', {'match': match, 'notes_form': notes_form, 'pk': pk
  })
  
@login_required
def add_note(request, pk):
  print('add note reached')
  form = NotesForm(request.POST)
  if form.is_valid():
    new_note = form.save(commit=False)
    new_note.match_id = pk
    new_note.save()
  return redirect('match_detail', pk=pk)

@login_required
def delete_note(request, note_id, pk):
  Match_notes.objects.filter(id=note_id).delete()
  return redirect('match_detail', pk=pk)

class MatchDelete(LoginRequiredMixin, DeleteView):
  model = Match
  success_url = '/matches/'

class MatchUpdate(LoginRequiredMixin, UpdateView):
  model = Match
  fields = ['name', 'email', 'phone_number', 'age', 'location', 'meet', 'interests', 'zodiac']
  # success_url ='/matches/'

  def get_success_url(self):
      # print('Self: ', self.request)
      print('ID: ', self.request.POST['match_id'])
      # return reverse('profile', kwargs={'pk': request.user.id})
      return f'/matches/{self.request.POST["match_id"]}'

class RdvCreate(LoginRequiredMixin, CreateView):
  template_name = 'main_app/rdv_form.html'
  form_class = RdvForm
  success_url = '/rdvs/'
  def get_form_kwargs(self):
    kwargs = super(RdvCreate, self).get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

class RdvList(LoginRequiredMixin, ListView):
  model = Rdv

class RdvDetail(LoginRequiredMixin, DetailView):
  model = Rdv

class RdvUpdate(LoginRequiredMixin, UpdateView):
  model = Rdv
  fields = ['match', 'date', 'rdv_time', 'what', 'where', 'rating']

class RdvDelete(LoginRequiredMixin, DeleteView):
  model = Rdv
  success_url= '/rdvs/'

@login_required
def user_detail(request, pk):
  profile = Profile.objects.filter(user=request.user)
  print(profile)
  return render(request, 'auth/user_detail.html', {'profile': profile}, pk)


class ProfileCreate (LoginRequiredMixin, CreateView):
  model = Profile
  fields = ['first_name', 'last_name', 'age', 'gender', 'zodiac', 'apps_used', 'relationship_goal']
  # success_url = f'/profile/{request.user.id}'

  def form_valid(self, form):
  # Assign the logged in user
    form.instance.user = self.request.user
    # Let the CreateView do its job as usual
    return super().form_valid(form)

  def get_success_url(self):
      # return reverse('profile', kwargs={'pk': request.user.id})
      return f'/profile/{self.request.user.id}'
  # def get_success_url(self):
  #   return (f'profile/{request.user.id}')

class ProfileUpdate(LoginRequiredMixin, UpdateView):
  model = Profile
  fields = ['first_name', 'last_name', 'age', 'gender', 'zodiac', 'apps_used', 'relationship_goal']

  # def get_object(self):
  #   return Profile.objects.get(pk=self.request.POST.get('pk'))

class ProfileDelete(LoginRequiredMixin, DeleteView):
  model = Profile
  success_url= '/matches/'

# Google Calendar API

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def cal(request, pk):
  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
          creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              'credentials.json', SCOPES)
          creds = flow.run_local_server()
      # Save the credentials for the next run
      with open('token.pickle', 'wb') as token:
          pickle.dump(creds, token)

  service = build('calendar', 'v3', credentials=creds)

  # Environment setup above, add event below
  rdv = Rdv.objects.get(pk=pk)

  if not rdv.rdv_time:
    rdv.rdv_time = '12:00:00'

  event = {
      'summary': f'Meet with {rdv.match.name}',
      'location': f'{rdv.where}',
      'description': f'{rdv.what}',
      'start': {
          'dateTime': f'{rdv.date}T{rdv.rdv_time}-07:00',
          'timeZone': 'America/Los_Angeles',
      },
      'end': {
          'dateTime': f'{rdv.date}T{rdv.rdv_time}-07:00',
          'timeZone': 'America/Los_Angeles',
      }
      }

  event = service.events().insert(calendarId='primary', body=event).execute()
  return redirect('rdv_detail', pk=pk)
  # print ('Event created: %s' % (event.get('htmlLink')))

def ghost(request, pk):
  match = Match.objects.get(pk=pk)
  if not match.ghost:
    match.ghost = True
  else :
    match.ghost = False
  match.save()
  # print(match.ghost)
  return redirect('match_detail', pk=pk)


# Yelp API below
def yelp(request, pk):
  # Trigger yelp
  api_key = 'RF_dcHA_yUIN-q03f0jTzj6LK_LYZ2wvhGYDuFTcpVepnKdrH2w7fYY76ouUVHz6n47qBMwyPTy79oMCFOUcNW4KhHvGNd_c4v0ZWv0sO2mBxqlkfYZGGI35yRIMXXYx'
  headers = {'Authorization': 'Bearer %s' % api_key}
  url = 'https://api.yelp.com/v3/businesses/search'
  rdv = Rdv.objects.get(pk=pk)
  params = {
    'term': f'{rdv.what}',
    'location': f'{rdv.where}',
    'limit': 5
  }
  req = requests.get(url, params=params, headers=headers)
  parsed = json.loads(req.text)
  businesses = parsed["businesses"]

  yelp_search = []

  for business in businesses:
    business = {
      'name': business['name'],
      'rating': business['rating'],
      'address': business['location']['address1'],
      'phone': business['phone'],
      'url': business['url']
    }
    yelp_search.append(business)

  return render(request, 'main_app/rdv_detail.html', {'rdv': rdv, 'yelp': yelp_search})


