"""
Run the evaluation suite and print the scores.

    python manage.py run_evals
    python manage.py run_evals --only policy
    python manage.py run_evals --limit 5
"""

from collections import defaultdict

from django.core.management.base import BaseCommand

from ai.evals import fixtures
from ai.evals.cases import CASES
from ai.evals.metrics import score
from ai.evals.runner import run_case


class Command(BaseCommand):
    help = "Run the AI evaluation suite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            default="",
            help="Only run cases whose id contains this.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Stop after this many cases. Useful while developing.",
        )

    def handle(self, *args, **options):
        # Fixed data first. Without it the scores move for reasons that
        # have nothing to do with the agent.
        fixtures.prepare()

        cases = [c for c in CASES if options["only"] in c.id]
        if options["limit"]:
            cases = cases[: options["limit"]]

        self.stdout.write(f"Running {len(cases)} cases\n")

        totals = defaultdict(lambda: [0, 0])  # name -> [passed, total]
        failures = []

        for index, case in enumerate(cases, start=1):
            run = run_case(case)
            checks = score(run)

            for check in checks:
                totals[check.name][1] += 1
                if check.passed:
                    totals[check.name][0] += 1
                else:
                    failures.append((case.id, check))

            mark = "." if all(c.passed for c in checks) else "F"
            self.stdout.write(mark, ending="")
            if index % 25 == 0:
                self.stdout.write("")

        self.stdout.write("\n")
        self._print_scores(totals)
        self._print_failures(failures)

    def _print_scores(self, totals):
        self.stdout.write("\nSCORES")
        overall_passed = overall_total = 0

        for name in ("tools", "refusal", "gate", "retrieval"):
            passed, total = totals.get(name, [0, 0])
            if not total:
                continue
            overall_passed += passed
            overall_total += total
            percent = 100 * passed / total
            self.stdout.write(f"  {name:10} {passed:3}/{total:<3} {percent:5.0f}%")

        if overall_total:
            percent = 100 * overall_passed / overall_total
            self.stdout.write(
                f"  {'overall':10} {overall_passed:3}/{overall_total:<3} {percent:5.0f}%"
            )

    def _print_failures(self, failures):
        if not failures:
            self.stdout.write(self.style.SUCCESS("\nNo failures."))
            return

        self.stdout.write(f"\nFAILURES ({len(failures)})")
        for case_id, check in failures:
            self.stdout.write(f"  {case_id:34} {check.name:10} {check.detail}")
