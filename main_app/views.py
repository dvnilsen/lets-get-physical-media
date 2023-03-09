from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Tape, Movie, User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
import requests

# Create your views here.


def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('/')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)


def home(request):
  return render(request, 'home.html')


def about(request):
  return render(request, 'about.html')

@login_required
def tapes_index(request):
  tapes = Tape.objects.filter(user=request.user)
  return render(request, 'tapes/index.html', {
    'tapes': tapes
  })



class TapeCreate(LoginRequiredMixin, CreateView):
  model = Tape
  fields = ['name', 'quantity', 'quality']

  def form_valid(self, form):
    form.instance.user = self.request.user 
    # Edward: this needs to eventually be
    return super().form_valid(form)
    # it was causing and error though 
    # return redirect('index')

@login_required
def tapes_detail(request, tape_id):
  tape = Tape.objects.get(id=tape_id)
  return render(request, 'tapes/detail.html', {
    'tape': tape })

class TapeUpdate(LoginRequiredMixin, UpdateView):
  model = Tape
  fields = ['quantity', 'quality']


class TapeDelete(LoginRequiredMixin, DeleteView):
  model = Tape
  success_url ='/tapes'


class MovieList(LoginRequiredMixin, ListView):
  model = Movie
  

class MovieDetail(LoginRequiredMixin, DetailView):
  model = Movie


class MovieUpdate(LoginRequiredMixin, UpdateView):
  model = Movie
  fields = '__all__'


class MovieDelete(LoginRequiredMixin, DeleteView):
  model = Movie
  success_url = '/movies'

class MovieCreate(LoginRequiredMixin, CreateView):
  model = Movie
  fields = '__all__'
  success_url ='/movies'

@login_required
def assoc_movie(request, tape_id, movie_id):
  Tape.objects.get(id=tape_id).movies.add(movie_id)
  return redirect('detail', tape_id=tape_id)

@login_required
def unassoc_movie(request, tape_id, movie_id):
  Tape.objects.get(id=tape_id).movies.remove(movie_id)
  return redirect('detail', tape_id=tape_id)


@login_required
def search_media(request):
  if request.method == 'POST':
    searched = request.POST['searched']
    movies = Movie.objects.filter(title__contains=searched)
    # moviesD = Movie.objects.filter(director__contains=searched)
    tapes = Tape.objects.filter(name__contains=searched)
    return render(request, 'search_media.html', {'searched': searched, 'movies': movies, 'tapes': tapes})
  else:
    return render(request, 'search_media.html', {})


def search_movies(request):
  if request.method == 'POST':
    searched = request.POST['searched']
    params = {'s': f'{searched}'}
    response=requests.get('http://www.omdbapi.com/?apikey=acd8ae1a&', params=params).json()
    search_response = response["Search"]
    return render(request, 'main_app/tape_form.html', {'searched': searched, 'search_response': search_response})
  else:
    return render(request, 'main_app/tape_form.html', {})
  

#def search_movies(request):

#   all_movies = {}
#   if request.method == 'POST':
#     searched = request.POST['searched']
#     params = {'s': f'{searched}'}
#     response=requests.get('http://www.omdbapi.com/?apikey=acd8ae1a&', params=params).json()
#     search_response = response["Search"]
#     for i in search_response:
#       movie_data = Movie(
#         title = i['Title'],
#         imdb_id = i['imdbID'],
#       )
#       movie_data.save()
#       all_movies = Movie.objects.all().order_by('-id')

#     return render(request, 'main_app/tape_form.html', {'searched': searched, 'search_response': search_response, 'all_movies': all_movies })
#   else:
#     return render(request, 'main_app/tape_form.html', {})
  

def assoc_tape(request):
  if request.method == 'POST':
    searched = request.POST['searched']
    params = {'i': f'{searched}'}
    imdb_response=requests.get('http://www.omdbapi.com/?apikey=acd8ae1a&', params=params).json()
    movie = Movie(
      title = imdb_response['Title'],
      imdb_id = imdb_response['imdbID'],
    )
    movie.save()
    tape = Tape(
      name = movie.title,
      quantity= 1,
      movie = movie,
      user = request.user 
    )
    tape.save()
    tape_id = tape.id

    return redirect('detail', tape_id=tape_id)
  else:
    return redirect(request, 'main_app/tape_form.html', {})
    
    


  # movie = Movie.objects.get(id=movie_id)
  # tape = Tape(
  #   name = movie.title,
  #   quantity= 1,
  #   movie = movie,
  #   user = request.user 
  # )
  # tape.save()
  # tape_id = tape.id
  # print(tape_id)
  # return redirect('detail', tape_id=tape_id)
  # return redirect('tapes_update', tape_id=tape_id)
  # return render(request, 'main_app/assoc_tape.html', { 'movie_id': movie_id, 'tape': tape, 'tape_id': tape_id })
  #
  #