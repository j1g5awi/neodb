import datetime
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from common.utils import GenerateDateUUIDMediaFilePath
from journal.exporters import CsvExporter, DoufenExporter, NdjsonExporter
from journal.importers import (
    DoubanImporter,
    GoodreadsImporter,
    LetterboxdImporter,
    OPMLImporter,
)
from journal.models import ShelfType, reset_journal_visibility_for_user
from social.models import reset_social_visibility_for_user
from takahe.utils import Takahe
from users.models import Task

from .account import clear_preference_cache


@login_required
def preferences(request):
    if not request.user.registration_complete:
        return redirect(reverse("users:register"))
    preference = request.user.preference
    identity = request.user.identity
    if request.method == "POST":
        identity.anonymous_viewable = bool(request.POST.get("anonymous_viewable"))
        identity.save(update_fields=["anonymous_viewable"])
        tidentity = Takahe.get_identity(identity.pk)
        tidentity.indexable = bool(request.POST.get("anonymous_viewable"))
        tidentity.save(update_fields=["indexable"])

        preference.default_visibility = int(request.POST.get("default_visibility"))
        preference.mastodon_default_repost = (
            int(request.POST.get("mastodon_default_repost", 0)) == 1
        )
        preference.classic_homepage = int(request.POST.get("classic_homepage"))
        preference.hidden_categories = request.POST.getlist("hidden_categories")
        preference.post_public_mode = int(request.POST.get("post_public_mode"))
        preference.show_last_edit = bool(request.POST.get("show_last_edit"))
        preference.mastodon_repost_mode = int(
            request.POST.get("mastodon_repost_mode", 0)
        )
        preference.mastodon_append_tag = request.POST.get(
            "mastodon_append_tag", ""
        ).strip()
        preference.save(
            update_fields=[
                "default_visibility",
                "post_public_mode",
                "classic_homepage",
                "mastodon_append_tag",
                "mastodon_repost_mode",
                "mastodon_default_repost",
                "show_last_edit",
                "hidden_categories",
            ]
        )
        lang = request.POST.get("language")
        if lang in dict(settings.LANGUAGES).keys() and lang != request.user.language:
            request.user.language = lang
            translation.activate(lang)
            request.LANGUAGE_CODE = translation.get_language()
            request.user.save(update_fields=["language"])
        clear_preference_cache(request)
    return render(
        request,
        "users/preferences.html",
        {"enable_local_only": settings.ENABLE_LOCAL_ONLY},
    )


@login_required
def data(request):
    if not request.user.registration_complete:
        return redirect(reverse("users:register"))
    current_year = datetime.date.today().year
    queryset = request.user.identity.shelf_manager.get_shelf(
        ShelfType.COMPLETE
    ).members.all()
    start_date = queryset.aggregate(Min("created_time"))["created_time__min"]
    start_year = start_date.year if start_date else current_year
    years = reversed(range(start_year, current_year + 1))
    return render(
        request,
        "users/data.html",
        {
            "allow_any_site": settings.MASTODON_ALLOW_ANY_SITE,
            "import_task": DoubanImporter.latest_task(request.user),
            "export_task": DoufenExporter.latest_task(request.user),
            "csv_export_task": CsvExporter.latest_task(request.user),
            "ndjson_export_task": NdjsonExporter.latest_task(request.user),
            "letterboxd_task": LetterboxdImporter.latest_task(request.user),
            "goodreads_task": GoodreadsImporter.latest_task(request.user),
            "years": years,
        },
    )


@login_required
def data_import_status(request):
    return render(
        request,
        "users/data_import_status.html",
        {
            "import_task": DoubanImporter.latest_task(request.user),
        },
    )


@login_required
def export_reviews(request):
    if request.method != "POST":
        return redirect(reverse("users:data"))
    return render(request, "users/data.html")


@login_required
def export_marks(request):
    if request.method == "POST":
        DoufenExporter.create(request.user).enqueue()
        messages.add_message(request, messages.INFO, _("Generating exports."))
        return redirect(reverse("users:data"))
    else:
        task = DoufenExporter.latest_task(request.user)
        if not task or task.state != Task.States.complete:
            messages.add_message(
                request, messages.ERROR, _("Export file not available.")
            )
            return redirect(reverse("users:data"))
        try:
            with open(task.metadata["file"], "rb") as fh:
                response = HttpResponse(
                    fh.read(), content_type="application/vnd.ms-excel"
                )
                response["Content-Disposition"] = 'attachment;filename="marks.xlsx"'
                return response
        except Exception:
            messages.add_message(
                request, messages.ERROR, _("Export file expired. Please export again.")
            )
            return redirect(reverse("users:data"))


@login_required
def export_csv(request):
    if request.method == "POST":
        task = CsvExporter.latest_task(request.user)
        if (
            task
            and task.state not in [Task.States.complete, Task.States.failed]
            and task.created_time > (timezone.now() - datetime.timedelta(hours=1))
        ):
            messages.add_message(
                request, messages.INFO, _("Recent export still in progress.")
            )
            return redirect(reverse("users:data"))
        CsvExporter.create(request.user).enqueue()
        messages.add_message(request, messages.INFO, _("Generating exports."))
        return redirect(reverse("users:data"))
    else:
        task = CsvExporter.latest_task(request.user)
        if not task or task.state != Task.States.complete:
            messages.add_message(
                request, messages.ERROR, _("Export file not available.")
            )
            return redirect(reverse("users:data"))
        response = HttpResponse()
        response["X-Accel-Redirect"] = (
            settings.MEDIA_URL + task.metadata["file"][len(settings.MEDIA_ROOT) :]
        )
        response["Content-Type"] = "application/zip"
        response["Content-Disposition"] = f'attachment; filename="{task.filename}.zip"'
        return response


@login_required
def export_ndjson(request):
    if request.method == "POST":
        task = NdjsonExporter.latest_task(request.user)
        if (
            task
            and task.state not in [Task.States.complete, Task.States.failed]
            and task.created_time > (timezone.now() - datetime.timedelta(hours=1))
        ):
            messages.add_message(
                request, messages.INFO, _("Recent export still in progress.")
            )
            return redirect(reverse("users:data"))
        NdjsonExporter.create(request.user).enqueue()
        messages.add_message(request, messages.INFO, _("Generating exports."))
        return redirect(reverse("users:data"))
    else:
        task = NdjsonExporter.latest_task(request.user)
        if not task or task.state != Task.States.complete:
            messages.add_message(
                request, messages.ERROR, _("Export file not available.")
            )
            return redirect(reverse("users:data"))
        response = HttpResponse()
        response["X-Accel-Redirect"] = (
            settings.MEDIA_URL + task.metadata["file"][len(settings.MEDIA_ROOT) :]
        )
        response["Content-Type"] = "application/zip"
        response["Content-Disposition"] = f'attachment; filename="{task.filename}.zip"'
        return response


@login_required
def sync_mastodon(request):
    if request.method == "POST":
        request.user.sync_accounts_later()
        messages.add_message(request, messages.INFO, _("Sync in progress."))
    return redirect(reverse("users:info"))


@login_required
def sync_mastodon_preference(request):
    if request.method == "POST":
        request.user.preference.mastodon_skip_userinfo = (
            request.POST.get("mastodon_sync_userinfo", "") == ""
        )
        request.user.preference.mastodon_skip_relationship = (
            request.POST.get("mastodon_sync_relationship", "") == ""
        )
        request.user.preference.save()
        messages.add_message(request, messages.INFO, _("Settings saved."))
    return redirect(reverse("users:info"))


@login_required
def reset_visibility(request):
    if request.method == "POST":
        visibility = int(request.POST.get("visibility"))
        visibility = visibility if visibility >= 0 and visibility <= 2 else 0
        reset_journal_visibility_for_user(request.user.identity, visibility)
        reset_social_visibility_for_user(request.user.identity, visibility)
        messages.add_message(request, messages.INFO, _("Reset completed."))
    return redirect(reverse("users:data"))


@login_required
def import_goodreads(request):
    if request.method == "POST":
        raw_url = request.POST.get("url")
        if GoodreadsImporter.validate_url(raw_url):
            GoodreadsImporter.create(
                request.user,
                visibility=int(request.POST.get("visibility", 0)),
                url=raw_url,
            ).enqueue()
            messages.add_message(request, messages.INFO, _("Import in progress."))
        else:
            messages.add_message(request, messages.ERROR, _("Invalid URL."))
    return redirect(reverse("users:data"))


@login_required
def import_douban(request):
    if request.method != "POST":
        return redirect(reverse("users:data"))
    f = (
        settings.MEDIA_ROOT
        + "/"
        + GenerateDateUUIDMediaFilePath("x.zip", settings.SYNC_FILE_PATH_ROOT)
    )
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "wb+") as destination:
        for chunk in request.FILES["file"].chunks():
            destination.write(chunk)
    if not DoubanImporter.validate_file(request.FILES["file"]):
        messages.add_message(request, messages.ERROR, _("Invalid file."))
        return redirect(reverse("users:data"))
    DoubanImporter.create(
        request.user,
        visibility=int(request.POST.get("visibility", 0)),
        mode=int(request.POST.get("import_mode", 0)),
        file=f,
    ).enqueue()
    messages.add_message(
        request, messages.INFO, _("File is uploaded and will be imported soon.")
    )
    return redirect(reverse("users:data"))


@login_required
def import_letterboxd(request):
    if request.method == "POST":
        f = (
            settings.MEDIA_ROOT
            + "/"
            + GenerateDateUUIDMediaFilePath("x.zip", settings.SYNC_FILE_PATH_ROOT)
        )
        os.makedirs(os.path.dirname(f), exist_ok=True)
        with open(f, "wb+") as destination:
            for chunk in request.FILES["file"].chunks():
                destination.write(chunk)
        LetterboxdImporter.create(
            request.user,
            visibility=int(request.POST.get("visibility", 0)),
            file=f,
        ).enqueue()
        messages.add_message(
            request, messages.INFO, _("File is uploaded and will be imported soon.")
        )
    return redirect(reverse("users:data"))


@login_required
def import_opml(request):
    if request.method == "POST":
        importer = OPMLImporter(
            request.user,
            int(request.POST.get("visibility", 0)),
            int(request.POST.get("import_mode", 0)),
        )
        if importer.import_from_file(request.FILES["file"]):
            messages.add_message(
                request, messages.INFO, _("File is uploaded and will be imported soon.")
            )
        else:
            messages.add_message(request, messages.ERROR, _("Invalid file."))
    return redirect(reverse("users:data"))
