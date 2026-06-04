from django.core.management.base import BaseCommand
from school.models import Athlete, AthleteQR

BATCH_SIZE = 5000

class Command(BaseCommand):
    help = "Generate QR identities safely"

    def handle(self, *args, **kwargs):

        batch = []

        existing_ids = set(
            AthleteQR.objects.values_list(
                'athlete_id',
                flat=True
            )
        )

        athletes = (
            Athlete.objects
            .exclude(id__in=existing_ids)
            .iterator(chunk_size=5000)
        )

        created = 0

        for athlete in athletes:

            batch.append(
                AthleteQR(athlete=athlete)
            )

            if len(batch) >= BATCH_SIZE:

                AthleteQR.objects.bulk_create(
                    batch,
                    batch_size=BATCH_SIZE
                )

                created += len(batch)

                self.stdout.write(
                    f"Created {created} QR identities..."
                )

                batch = []

        # remaining batch
        if batch:

            AthleteQR.objects.bulk_create(
                batch,
                batch_size=BATCH_SIZE
            )

            created += len(batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Total created: {created}"
            )
        )