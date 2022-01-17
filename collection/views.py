import logging
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils import timezone
from django.core.paginator import Paginator
from mastodon import mastodon_request_included
from mastodon.models import MastodonApplication
from mastodon.api import post_toot, TootVisibilityEnum
from mastodon.utils import rating_to_emoji
from common.utils import PageLinksGenerator
from common.views import PAGE_LINK_NUMBER, jump_or_scrape
from common.models import SourceSiteEnum
from .models import *
from .forms import *
from django.conf import settings
import re
from users.models import User
from django.http import HttpResponseRedirect



logger = logging.getLogger(__name__)
mastodon_logger = logging.getLogger("django.mastodon")


# how many marks showed on the detail page
MARK_NUMBER = 5
# how many marks at the mark page
MARK_PER_PAGE = 20
# how many reviews showed on the detail page
REVIEW_NUMBER = 5
# how many reviews at the mark page
REVIEW_PER_PAGE = 20
# max tags on detail page
TAG_NUMBER = 10


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['HX-Redirect'] = self['Location']
    status_code = 200


# public data
###########################
@login_required
def create(request):
    if request.method == 'GET':
        form = CollectionForm()
        return render(
            request,
            'create_update.html',
            {
                'form': form,
                'title': _('添加收藏单'),
                'submit_url': reverse("collection:create"),
                # provided for frontend js
                'this_site_enum_value': SourceSiteEnum.IN_SITE.value,
            }
        )
    elif request.method == 'POST':
        if request.user.is_authenticated:
            # only local user can alter public data
            form = CollectionForm(request.POST, request.FILES)
            form.instance.owner = request.user
            if form.is_valid():
                form.instance.last_editor = request.user
                try:
                    with transaction.atomic():
                        form.save()
                except IntegrityError as e:
                    logger.error(e.__str__())
                    return HttpResponseServerError("integrity error")
                return redirect(reverse("collection:retrieve", args=[form.instance.id]))
            else:
                return render(
                    request,
                    'create_update.html',
                    {
                        'form': form,
                        'title': _('添加收藏单'),
                        'submit_url': reverse("collection:create"),
                        # provided for frontend js
                        'this_site_enum_value': SourceSiteEnum.IN_SITE.value,
                    }
                )
        else:
            return redirect(reverse("users:login"))
    else:
        return HttpResponseBadRequest()


@login_required
def update(request, id):
    page_title = _("修改收藏单")
    collection = get_object_or_404(Collection, pk=id)
    if not collection.is_visible_to(request.user):
        raise PermissionDenied()
    if request.method == 'GET':
        form = CollectionForm(instance=collection)
        return render(
            request,
            'create_update.html',
            {
                'form': form,
                'title': page_title,
                'submit_url': reverse("collection:update", args=[collection.id]),
                # provided for frontend js
                'this_site_enum_value': SourceSiteEnum.IN_SITE.value,
            }
        )
    elif request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.instance.last_editor = request.user
            form.instance.edited_time = timezone.now()
            try:
                with transaction.atomic():
                    form.save()
            except IntegrityError as e:
                logger.error(e.__str__())
                return HttpResponseServerError("integrity error")
        else:
            return render(
                request,
                'create_update.html',
                {
                    'form': form,
                    'title': page_title,
                    'submit_url': reverse("collection:update", args=[collection.id]),
                    # provided for frontend js
                    'this_site_enum_value': SourceSiteEnum.IN_SITE.value,
                }
            )
        return redirect(reverse("collection:retrieve", args=[form.instance.id]))

    else:
        return HttpResponseBadRequest()


@mastodon_request_included
# @login_required
def retrieve(request, id):
    if request.method == 'GET':
        collection = get_object_or_404(Collection, pk=id)
        if not collection.is_visible_to(request.user):
            raise PermissionDenied()
        form = CollectionForm(instance=collection)

        followers = []
        if request.user.is_authenticated:
            followers = []

        return render(
            request,
            'detail.html',
            {
                'collection': collection,
                'form': form,
                'editable': collection.is_editable_by(request.user),
                'followers': followers,

            }
        )
    else:
        logger.warning('non-GET method at /collections/<id>')
        return HttpResponseBadRequest()


@mastodon_request_included
# @login_required
def retrieve_entity_list(request, id):
    collection = get_object_or_404(Collection, pk=id)
    if not collection.is_visible_to(request.user):
        raise PermissionDenied()
    form = CollectionForm(instance=collection)

    followers = []
    if request.user.is_authenticated:
        followers = []

    return render(
        request,
        'entity_list.html',
        {
            'collection': collection,
            'form': form,
            'editable': collection.is_editable_by(request.user),
            'followers': followers,

        }
    )


@permission_required("collections.delete_collection")
@login_required
def delete(request, id):
    collection = get_object_or_404(Collection, pk=id)
    if request.method == 'GET':
        return render(
            request,
            'collections/delete.html',
            {
                'collection': collection,
            }
        )
    elif request.method == 'POST':
        if request.user.is_staff or request.user == collection.owner:
            collection.delete()
            return redirect(reverse("common:home"))
        else:
            raise PermissionDenied()
    else:
        return HttpResponseBadRequest()


@login_required
def follow(request, id):
    pass


@login_required
def unfollow(request, id):
    pass


@login_required
def list(request, user_id=None):
    if request.method == 'GET':
        queryset = Collection.objects.filter(owner=request.user if user_id is None else User.objects.get(id=user_id))
        paginator = Paginator(queryset, REVIEW_PER_PAGE)
        page_number = request.GET.get('page', default=1)
        reviews = paginator.get_page(page_number)
        reviews.pagination = PageLinksGenerator(
            PAGE_LINK_NUMBER, page_number, paginator.num_pages)
        return render(
            request,
            'list.html',
            {
                'collections': queryset,
            }
        )
    else:
        return HttpResponseBadRequest()


def get_entity_by_url(url):
    m = re.findall(r'^/?(movies|books|games|music/album|music/song)/(\d+)/?', url.strip().lower().replace(settings.APP_WEBSITE.lower(), ''))
    if len(m) > 0:
        mapping = {
            'movies': Movie,
            'books': Book,
            'games': Game,
            'music/album': Album,
            'music/song': Song,
        }
        cls = mapping.get(m[0][0])
        id = int(m[0][1])
        if cls is not None:
            return cls.objects.get(id=id)
    return None


@login_required
def append_item(request, id):
    collection = get_object_or_404(Collection, pk=id)
    if request.method == 'POST' and collection.is_editable_by(request.user):
        url = request.POST.get('url')
        comment = request.POST.get('comment')
        item = get_entity_by_url(url)
        collection.append_item(item, comment)
        collection.save()
        # return redirect(reverse("collection:retrieve", args=[id]))
        return retrieve_entity_list(request, id)
    else:
        return HttpResponseBadRequest()


@login_required
def delete_item(request, id, item_id):
    collection = get_object_or_404(Collection, pk=id)
    if request.method == 'POST' and collection.is_editable_by(request.user):
        # item_id = int(request.POST.get('item_id'))
        item = CollectionItem.objects.get(id=item_id)
        if item is not None and item.collection == collection:
            item.delete()
            # collection.save()
        # return HTTPResponseHXRedirect(redirect_to=reverse("collection:retrieve", args=[id]))
        return retrieve_entity_list(request, id)
    return HttpResponseBadRequest()


@login_required
def move_up_item(request, id, item_id):
    collection = get_object_or_404(Collection, pk=id)
    if request.method == 'POST' and collection.is_editable_by(request.user):
        # item_id = int(request.POST.get('item_id'))
        item = CollectionItem.objects.get(id=item_id)
        if item is not None and item.collection == collection:
            items = collection.collectionitem_list
            idx = items.index(item)
            if idx > 0:
                o = items[idx - 1]
                p = o.position
                o.position = item.position
                item.position = p
                o.save()
                item.save()
                # collection.save()
        # return HTTPResponseHXRedirect(redirect_to=reverse("collection:retrieve", args=[id]))
        return retrieve_entity_list(request, id)
    return HttpResponseBadRequest()


@login_required
def move_down_item(request, id, item_id):
    collection = get_object_or_404(Collection, pk=id)
    if request.method == 'POST' and collection.is_editable_by(request.user):
        # item_id = int(request.POST.get('item_id'))
        item = CollectionItem.objects.get(id=item_id)
        if item is not None and item.collection == collection:
            items = collection.collectionitem_list
            idx = items.index(item)
            if idx + 1 < len(items):
                o = items[idx + 1]
                p = o.position
                o.position = item.position
                item.position = p
                o.save()
                item.save()
                # collection.save()
        # return HTTPResponseHXRedirect(redirect_to=reverse("collection:retrieve", args=[id]))
        return retrieve_entity_list(request, id)
    return HttpResponseBadRequest()


def show_item_comment(request, id, item_id):
    collection = get_object_or_404(Collection, pk=id)
    item = CollectionItem.objects.get(id=item_id)
    editable = collection.is_editable_by(request.user)
    return render(request, 'show_item_comment.html', {'collection': collection, 'item': item, 'editable': editable})

@login_required
def update_item_comment(request, id, item_id):
    collection = get_object_or_404(Collection, pk=id)
    if collection.is_editable_by(request.user):
        # item_id = int(request.POST.get('item_id'))
        item = CollectionItem.objects.get(id=item_id)
        if item is not None and item.collection == collection:
            if request.method == 'POST':
                item.comment = request.POST.get('comment', default='')
                item.save()
                return render(request, 'show_item_comment.html', {'collection': collection, 'item': item, 'editable': True})
            else:
                return render(request, 'edit_item_comment.html', {'collection': collection, 'item': item})
        return retrieve_entity_list(request, id)
    return HttpResponseBadRequest()


@login_required
def list_with(request, type, id):
    pass


def get_entity_by_type_id(type, id):
    mapping = {
        'movie': Movie,
        'book': Book,
        'game': Game,
        'album': Album,
        'song': Song,
    }
    cls = mapping.get(type)
    if cls is not None:
        return cls.objects.get(id=id)
    return None


@login_required
def add_to_list(request, type, id):
    item = get_entity_by_type_id(type, id)
    if request.method == 'GET':
        queryset = Collection.objects.filter(owner=request.user)
        return render(
            request,
            'add_to_list.html',
            {
                'type': type,
                'id': id,
                'item': item,
                'collections': queryset,
            }
        )
    else:
        collection = Collection.objects.filter(owner=request.user, id=request.POST.get('collection_id')).first()
        collection.append_item(item, request.POST.get('comment'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))