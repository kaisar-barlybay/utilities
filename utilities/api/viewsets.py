import traceback
from ..time import Timer
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework.request import Request
from typing import Any, Union, List, Tuple, TypedDict
from ..base import Base
from django.core.exceptions import ValidationError
from rest_framework import permissions, viewsets, serializers, status
from rest_framework.serializers import BaseSerializer

from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
import logging
logger = logging.getLogger('default')


class TContext(TypedDict, total=False):
  request: Request


class Pagination(PageNumberPagination):
  page_size = 10
  page_size_query_param = 'page_size'
  max_page_size = 10

  def get_paginated_response(self, data: Any, meta: Union[dict, None] = None, page_size: Union[int, None] = None) -> Response:
    return Response(OrderedDict([
        ('next', self.get_next_link()),
        ('count', self.page.paginator.count),
        ('previous', self.get_previous_link()),
        ('results', data),
        ('meta', meta),
        ('page_size', page_size),
    ]))


class model_serializer(serializers.ModelSerializer):
  exclude_fields: List[str] = []

  @property
  def context(self) -> (Any | TContext):
    return super().context

  @staticmethod
  def filter_fields(fields: List[str], exclude_fields: List[str] = [], append_fields: List[str] = []) -> List[str]:
    return [n for n in fields if n not in exclude_fields] + append_fields

  def is_valid(self, raise_exception: bool = False, instance: Any = None) -> bool:
    validation = super().is_valid(raise_exception=raise_exception)
    return validation


class modelViewSet(viewsets.ModelViewSet, Base):

  serializer_class: type[model_serializer] = model_serializer()

  pagination_class = Pagination
  permission_classes = [permissions.IsAuthenticated]

  debug = False

  def get_paginated_response(self, data: Any, meta: Union[None, dict] = None) -> Union[Response, None]:
    page_size = int(self.request.GET.get('page_size', 10))
    self.pagination_class.page_size = page_size
    self.pagination_class.max_page_size = page_size
    assert self.paginator is not None
    return self.paginator.get_paginated_response(data, meta, page_size)

  def __init__(self, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self.serializers: dict[str, model_serializer] = {}

  def get_integrity_error_message(self, instance: Any) -> str:
    return f""

  def get_serializer(self, *args, **kwargs):
    def handle_view(serializer_name: str) -> Union[None, str]:
      view = None
      if serializer_name in kwargs:
        view = kwargs[serializer_name]
        del kwargs[serializer_name]
      return view
    serializer_class = self.get_serializer_class(
        view=handle_view('view'),
        row=handle_view('row'),
        element=handle_view('element'),
        item=handle_view('item'),
    )
    kwargs.setdefault('context', self.get_serializer_context())
    return serializer_class(*args, **kwargs)

  def get_serializer_class(self,
                           view: Union[str, None] = None,
                           row: Union[str, None] = None,
                           element: Union[str, None] = None,
                           item: Union[str, None] = None,
                           ):
    assert self.serializer_class is not None, (
        "'%s' should either include a `serializer_class` attribute, "
        "or override the `get_serializer_class()` method."
        % self.__class__.__name__
    )
    if view is not None:
      return self.serializers[view]
    if row is not None:
      return self.serializers[row]
    if element is not None:
      return self.serializers[element]
    if item is not None:
      return self.serializers[item]

    return self.serializer_class

  def get_integrity_params(self, instance: Any) -> dict[Union[str, int], Union[str, int]]:
    return {}

  def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    partial = kwargs.pop('partial', False)
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
    try:
      serializer.is_valid(instance=instance, raise_exception=True)
    except ValidationError as e:
      res = {
          "message": e.message,
          "params": e.params,
      }
      return Response(data=res, status=e.code)
    instance = self.perform_update(serializer)
    serializer_response = self.get_serializer(
        instance,
        view=request.GET.get('view', None),
        row=request.GET.get('row', None),
        element=request.GET.get('element', None),
        item=request.GET.get('item', None),
        context={'request': request},
    )

    if getattr(instance, '_prefetched_objects_cache', None):
      instance._prefetched_objects_cache = {}
    return Response(serializer_response.data)

  def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    serializer = self.get_serializer(data=request.data, context={'request': request})
    try:
      serializer.is_valid(instance=None, raise_exception=True)
    except ValidationError as e:
      res = {
          "message": e.message,
          "params": e.params,
      }
      return Response(data=res, status=e.code)
    instance = self.perform_create(serializer)
    qs, meta = self.get_queryset()
    try:
      instance = qs.get(id=instance.id)
    except Exception as e:
      pass
    serializer_response = self.get_serializer(
        instance,
        view=request.GET.get('view', None),
        row=request.GET.get('row', None),
        element=request.GET.get('element', None),
        item=request.GET.get('item', None),
        context={'request': request},
    )
    headers = self.get_success_headers(serializer_response.data)
    return Response(serializer_response.data, status=status.HTTP_201_CREATED, headers=headers)

  def handle_integrity_error(self, instance: Any, e: IntegrityError) -> Tuple[int, Union[str, None], dict]:
    return status.HTTP_409_CONFLICT, None, {}

  def destroy(self, request: Request, *message: Any, **kwargs: Any) -> Response:
    instance = self.get_object()
    try:
      self.perform_destroy(instance)
    except IntegrityError as e:
      st, message, params = self.handle_integrity_error(instance, e)
      if message is None:
        logger.error(f"[ERROR] [{traceback.format_exc()}] {e}")
      res = {"message": message if message is not None else '', "params": params}
      return Response(data=res, status=st)
    return Response(status=status.HTTP_204_NO_CONTENT)

  def get_object(self):
    """
    Returns the object the view is displaying.

    You may want to override this if you need to provide non-standard
    queryset lookups.  Eg if objects are referenced using multiple
    keyword arguments in the url conf.
    """
    qs, meta = self.get_queryset()
    queryset = self.filter_queryset(qs)

    # Perform the lookup filtering.
    lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

    assert lookup_url_kwarg in self.kwargs, (
        'Expected view %s to be called with a URL keyword argument '
        'named "%s". Fix your URL conf, or set the `.lookup_field` '
        'attribute on the view correctly.' %
        (self.__class__.__name__, lookup_url_kwarg)
    )

    filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
    obj = get_object_or_404(queryset, **filter_kwargs)

    # May raise a permission denied
    self.check_object_permissions(self.request, obj)

    return obj

  def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    instance = self.get_object()
    serializer = self.get_serializer(
        instance,
        view=request.GET.get('view', None),
        row=request.GET.get('row', None),
        element=request.GET.get('element', None),
        item=request.GET.get('item', None),
        context={'request': request},
    )
    return Response(serializer.data)

  def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    timer = Timer(self.debug)
    qs, meta = self.get_queryset()
    queryset = self.filter_queryset(qs)
    view = request.GET.get('view', None)
    row = request.GET.get('row', None)
    element = request.GET.get('element', None)
    item = request.GET.get('item', None)
    page_number = request.query_params.get(self.pagination_class.page_query_param, None)
    # logger.warning(f"{self.__class__.__name__}: {view}")
    task_id = f'query {self.serializer_class.Meta.model.__name__} list view'
    timer.start(task_id)
    if page_number is not None:
      page = self.paginate_queryset(queryset)
      serializer = self.get_serializer(page, many=True, view=view, row=row, element=element, item=item)
      response = self.get_paginated_response(serializer.data, meta)
      timer.finish(task_id)
      return response

    serializer = self.get_serializer(queryset, many=True, view=view, row=row, element=element, item=item, context={'request': request})
    timer.finish(task_id)
    return Response(serializer.data)

  def perform_create(self, serializer: BaseSerializer[Any]) -> Any:
    return serializer.save()

  def perform_update(self, serializer: BaseSerializer[Any]) -> Any:
    return serializer.save()
