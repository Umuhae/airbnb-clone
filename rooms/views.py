from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, View, UpdateView, FormView
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from users import mixins as user_mixins
from . import models, forms
from reservations import models as reservations
from reviews import forms as review_forms
from conversations import views as con_view

class HomeView(ListView):

    """ HomeView Definition """

    model = models.Room
    paginate_by = 12
    # paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"


class RoomDetail(DetailView, con_view.ConversationDetailView):

    """ RoomDetail Definition """

    model = models.Room

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = review_forms.CreateReviewForm()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = forms.CreateReviewForm(request.POST)
        pk = self.kwargs.get("pk")
        room = models.Room.objects.get(pk=pk)


class SearchView(View):

    """ SearchView Definition """

    def get(self, request):
        country = request.GET.get("country")
        if country:

            form = forms.SearchForm(request.GET)

            if form.is_valid():

                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity

                for facility in facilities:
                    filter_args["facilities"] = facility

                qs = models.Room.objects.filter(**filter_args).order_by("-created")

                paginator = Paginator(qs, 1)

                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)
                print(dir(rooms),dir(form))
                return render(
                    request, "rooms/search.html", {"form": form, "rooms": rooms}
                )

        else:
            form = forms.SearchForm()

        return render(request, "rooms/search.html", {"form": form})

class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):
    model = models.Room
    template_name = 'rooms/room_edit.html'
    fields = (
        'name',
        'description',
        'country',
        'city',
        'price',
        'address',
        'guests',
        'beds',
        'bedrooms',
        'baths',
        'check_in',
        'check_out',
        'instant_book',
        'room_type',
        'amenities',
        'facilities',
        'house_rules',
    )

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

class RoomPhotosView(user_mixins.LoggedInOnlyView, RoomDetail):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Cant delete that photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Cant delete that photo")

        return redirect(reverse ("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = 'photo_pk'
    fields = (
        'caption',
        'file',
    )
    success_message = "Photo Updated"
    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={'pk': room_pk})

class AddPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, FormView):

    model = models.Photo
    template_name = 'rooms/photo_create.html'
    fields = ("file", "caption")
    form_class = forms.CreatePhotoForm

