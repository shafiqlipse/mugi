from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps
import uuid 
from accounts.models import *
# Create your models here.
import uuid

from django.conf import settings
from django.db import models

# Defined once and shared, so Respondent.department and Ticket.topic can't drift apart.
TOPIC_CHOICES = [
    ("General", "General"),          # default / unrouted tickets
    ("Registration", "Registration"),
    ("Athletes", "Athletes"),
    ("Officials", "Officials"),
    ("Enrollments", "Enrollments"),
    ("Payments", "Payments"),
    ("Championships", "Championships"),
]

STATUS_CHOICES = [
    ("Open", "Open"),
    ("Picked up", "Picked up"),
    ("Answered", "Answered"),                  # staff replied, waiting on school
    ("School Response", "School Response"),    # school replied, waiting on staff
    ("Closed", "Closed"),
]

PRIORITY_CHOICES = [
    ("Urgent", "Urgent"),
    ("High", "High"),
    ("Medium", "Medium"),
    ("Low", "Low"),
]


class Respondent(models.Model):
    """A support staff member and the department whose tickets they handle."""

    # OneToOne: one user = one respondent profile = one department
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=122)
    lname = models.CharField(max_length=122)
    department = models.CharField(max_length=20, choices=TOPIC_CHOICES, default="General")

    def __str__(self):
        return f"{self.fname} {self.lname}"


class TicketQuerySet(models.QuerySet):
    def for_staff(self, user):
        """Superusers see everything; other staff see only their department's tickets.
        A user without a Respondent profile sees nothing."""
        if user.is_superuser:
            return self.all()
        return self.filter(
            topic__in=Respondent.objects.filter(user=user).values_list("department", flat=True)
        )


class Ticket(models.Model):
    title = models.CharField(max_length=100)
    sender = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="tickets"
    )
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, default="General")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="Medium")
    ticket_id = models.CharField(max_length=12, unique=True, editable=False)

    # Who picked it up (set this when status becomes "Picked up")
    assigned_to = models.ForeignKey(
        Respondent, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_tickets",
    )
    # Optional but recommended for per-school reporting; users change schools,
    # so store it on the ticket. Replace with your real school model, then migrate:
    # school = models.ForeignKey("schools.School", null=True, blank=True,
    #                            on_delete=models.PROTECT, related_name="tickets")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TicketQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            while True:  # retry in the (unlikely) event of a collision
                candidate = f"#{uuid.uuid4().hex[:8].upper()}"
                if not Ticket.objects.filter(ticket_id=candidate).exists():
                    self.ticket_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} {self.title}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="responses")
    # One author for every message, school or staff. Staff status comes from
    # author.is_staff, so no separate responder / school_responder fields.
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="ticket_messages"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Only on a new message, and never reopen a closed ticket
        ticket = self.ticket
        if is_new and ticket.status != "Closed":
            fields = ["status", "updated_at"]
            if self.author.is_staff:
                ticket.status = "Answered"
                # First staff reply claims an unassigned ticket
                if ticket.assigned_to_id is None:
                    respondent = Respondent.objects.filter(user=self.author).first()
                    if respondent:
                        ticket.assigned_to = respondent
                        fields.append("assigned_to")
            else:
                ticket.status = "School Response"
            ticket.save(update_fields=fields)

    def __str__(self):
        name = self.author.get_full_name() or self.author.get_username()
        return f"Message from {name} on {self.ticket.title}"