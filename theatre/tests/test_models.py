from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from theatre.models import (
    Genre,
    Actor,
    TheatreHall,
    Play,
    Performance,
    Reservation,
    Ticket,
)


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Blue", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


class ModelsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword",
        )
        self.client.force_authenticate(self.user)

        self.genre = Genre.objects.create(name="Ballet")
        self.actor = Actor.objects.create(first_name="Test", last_name="Actor")
        self.theatre_hall = TheatreHall.objects.create(
            name="main stage",
            rows=10,
            seats_in_row=8
        )

    def test_actor_str(self):
        self.assertEqual(str(self.actor), "Test Actor")

    def test_genre_str(self):
        self.assertEqual(str(self.genre), "Ballet")

    def test_theatre_hall_str(self):
        self.assertEqual(str(self.theatre_hall), "main stage")

    def test_play_str(self):
        play = sample_play()
        play.genres.add(self.genre)
        play.actors.add(self.actor)

        self.assertEqual(str(play), "Sample play")

    def test_performance_str(self):
        play = sample_play()
        play.genres.add(self.genre)
        play.actors.add(self.actor)
        performance = sample_performance(play=play)

        self.assertEqual(str(performance), "Sample play 2022-06-02 14:00:00")

    def test_reservation_str(self):
        reservation = Reservation.objects.create(
            user=self.user
        )

        expected_str = str(timezone.now().replace(microsecond=0))
        reservation_str = str(reservation.created_at.replace(microsecond=0))
        self.assertEqual(reservation_str, expected_str)

    def test_ticket_str(self):
        play = sample_play()
        play.genres.add(self.genre)
        play.actors.add(self.actor)
        performance = sample_performance(play=play)
        reservation = Reservation.objects.create(
            user=self.user
        )
        ticket = Ticket.objects.create(
             performance=performance,
             reservation=reservation,
             row=3,
             seat=4,
        )

        try:
            ticket.clean()
        except ValidationError:
            self.fail("validate_ticket raised ValidationError incorrectly.")
        self.assertEqual(str(ticket),
                         f"{str(ticket.performance)} "
                         f"(row: {ticket.row}, seat: {ticket.seat})")
