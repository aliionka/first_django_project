import os

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import FileSystemStorage

from .forms import UserBioForm


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
    context = {}
    if request.method == "POST":
        if not request.FILES.get("myfile"):
            context["error"] = "Пожалуйста, выберите файл"
        else:
            myfile = request.FILES.get("myfile")

            # Проверка расширения
            extension = os.path.splitext(myfile.name)[1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                context["error"] = f"Недопустимый тип файла! Разрешенные: {', '.join(ALLOWED_EXTENSIONS)}"
                return render(request, "requestdataapp/file-upload.html", context)

            else:
                if myfile.size > MAX_SIZE:
                    context["error"] = f"Файл слишком большой! Максимальный размер: {MAX_SIZE // (1024*1024)} MB"
                    return render(request, "requestdataapp/file-upload.html", context)

                # Проверка MIME-типа
                if myfile.content_type and myfile.content_type not in ALLOWED_MIME_TYPES:
                    context["error"] = f"Недопустимый MIME-тип файла! Разрешенные: {', '.join(ALLOWED_MIME_TYPES)}"
                    return render(request, "requestdataapp/file-upload.html", context)

                # Сохранение файла
                try:
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    context["success"] = f"Файл {filename} успешно загружен!"
                    context["file_info"] = {
                        "original_name": myfile.name,
                        "saved_name": filename,
                        "size_kb": round(myfile.size / 1024, 2),  # Размер в КБ
                        "content_type": myfile.content_type,
                    }

                except Exception as e:
                    context["error"] = f"Ошибка при сохранении файла: {str(e)}"

    return render(request, "requestdataapp/file-upload.html", context)


def test_view(request):
    """Простая тестовая view для проверки throttling"""
    return HttpResponse("OK")