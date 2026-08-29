from pathlib import Path
from django.db import transaction
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from ai.ingest import ingest
from ai.models import KnowledgeDocument
from employees.models import Employee


class Command(BaseCommand):
    help = "Load a document into the assistant's searchable knowledge base."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to a .pdf, .txt or .md file")
        parser.add_argument("--title", help="Defaults to the file name")
        parser.add_argument(
            "--employee",
            help="Employee ID such as EMP001. Omit for a company-wide document.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"No such file: {path}")

        employee = None
        if options["employee"]:
            employee = Employee.objects.filter(
                employee_id=options["employee"]
            ).first()
            if employee is None:
                raise CommandError(f"No employee with ID {options['employee']}")

        # The document row and its chunks are one unit. Without this, a
        # failed embed call leaves an empty document behind — as happened
        # twice while EMBEDDING_MODEL was wrong.
        with transaction.atomic():
            document = KnowledgeDocument(
                title=options["title"] or path.stem,
                employee=employee,
            )
            with path.open("rb") as handle:
                document.file.save(path.name, File(handle), save=False)
            document.save()

            count = ingest(document)

        who = employee.employee_id if employee else "everyone"

        self.stdout.write(
            self.style.SUCCESS(
                f"Indexed '{document.title}' into {count} chunks — readable by {who}."
            )
        )
