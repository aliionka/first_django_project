import logging
import os
from django.core.exceptions import ValidationError

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import FileSystemStorage

from .forms import UserBioForm, FileUploadForm

logger = logging.getLogger(__name__)


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)


MAX_SIZE = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.docx', '.xlsx', '.txt']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    """Обработчик загрузки файлов с валидацией и обработкой ошибок"""

    context = {}

    if request.method != "POST":
        return render(request, "requestdataapp/file-upload.html", context)

    # Проверка наличия файла
    myfile = request.FILES.get("myfile")
    if not myfile:
        context["error"] = "Пожалуйста, выберите файл"
        return render(request, "requestdataapp/file-upload.html", context)

    # Валидация через форму
    form = FileUploadForm(request.POST, request.FILES)

    try:
        # Проверка валидности формы
        if not form.is_valid():
            context["error"] = " | ".join(
                [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
            )
            return render(request, "requestdataapp/file-upload.html", context)

        # Проверка расширения
        extension = os.path.splitext(myfile.name)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            context["error"] = f"Недопустимый тип файла! Разрешенные: {', '.join(ALLOWED_EXTENSIONS)}"
            return render(request, "requestdataapp/file-upload.html", context)

        # Проверка размера файла
        if myfile.size > MAX_SIZE:
            context["error"] = f"Файл слишком большой! Максимальный размер: {MAX_SIZE // (1024 * 1024)} МБ"
            return render(request, "requestdataapp/file-upload.html", context)

        # Проверка MIME-типа
        content_type = getattr(myfile, 'content_type', None)
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            context["error"] = f"Недопустимый MIME-тип файла! Разрешенные: {', '.join(ALLOWED_MIME_TYPES)}"
            return render(request, "requestdataapp/file-upload.html", context)

        # Сохранение файла с обработкой конфликтов имен
        fs = FileSystemStorage()

        # Генерация безопасного имени файла
        safe_filename = fs.get_available_name(myfile.name)

        filename = fs.save(safe_filename, myfile)

        # Подготовка информации о файле для контекста
        context["success"] = f"Файл {filename} успешно загружен!"
        context["file_info"] = {
            "original_name": myfile.name,
            "saved_name": filename,
            "size_kb": round(myfile.size / 1024, 2),
            "content_type": myfile.content_type if hasattr(myfile, 'content_type') else "unknown",
            "file_size_readable": _format_file_size(myfile.size),
        }

        # Логирование успешной загрузки
        logger.info(
            f"File uploaded: {filename} (original: {myfile.name}), "
            f"size: {myfile.size} bytes, type: {myfile.content_type or 'unknown'}"
        )

    except ValidationError as e:
        context["error"] = f"Ошибка валидации: {', '.join(e.messages)}"
        logger.warning(f"Validation error during file upload: {e}")

    except PermissionError as e:
        context["error"] = "Ошибка доступа при сохранении файла. Пожалуйста, обратитесь к администратору."
        logger.error(f"Permission error during file upload: {e}")

    except Exception as e:
        context["error"] = f"Неожиданная ошибка при сохранении файла. Пожалуйста, попробуйте позже."
        logger.error(f"Unexpected error during file upload: {e}", exc_info=True)

    return render(request, "requestdataapp/file-upload.html", context)


def _format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def test_view(request):
    """Простая тестовая view для проверки throttling"""
    return HttpResponse("OK")
