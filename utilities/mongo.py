from io import BufferedReader, BytesIO
import logging
from typing import Any, Union
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from mongoengine import Document  # type: ignore


logger = logging.getLogger(__name__)


IStream = Union[BufferedReader, TemporaryUploadedFile, InMemoryUploadedFile, BytesIO]


class MongoStorage:
  def __init__(self, model: Document) -> None:
    self.model = model

  def insert_file(self, stream: IStream) -> str:
    f = self.model.objects.create()
    with stream as fd:
      f.path.put(fd)
    f.save()
    return f.id

  def create_from_bytes(self, instance: Any, field_name: str, stream: IStream) -> Document:
    f = self.model.objects.create()
    with stream as fd:
      f.path.put(fd)
    f.save()
    setattr(instance, field_name, f.id)
    instance.save()
    return f

  def get_bytes(self, instance: Any, field_name: str) -> Union[IStream, None]:
    file_id = getattr(instance, field_name)
    if file_id is None:
      return None

    f = self.model.objects.get(id=file_id)
    return f.path.read()

  def delete(self, instance: Any, field_name: str) -> None:
    file_id = getattr(instance, field_name)
    if file_id is None:
      return None

    f = self.model.objects.get(id=file_id)
    f.delete()
    setattr(instance, field_name, None)
    instance.save()

  def update_from_bytes(self, instance: Any, field_name: str, stream: IStream) -> Document:
    file_id = getattr(instance, field_name)
    if file_id is not None:
      logger.info('%s is not empty => updating file', file_id)
      f = self.model.objects.get(id=file_id)
      with stream as fd:
        f.path.replace(fd)
      f.save()
      setattr(instance, field_name, f.id)
    else:
      f = self.create_from_bytes(instance, field_name, stream)
    return f
