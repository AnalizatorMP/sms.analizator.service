import json

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
from loguru import logger

from users_app.forms import ServiceForm, ServiceKeyForm
from users_app.models import NumbersService, Rules, Key, User
from utils.logger_config import log_request, log_webhook_request, api_logger


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"Успешный вход пользователя: {user.phone} (ID: {user.id})")
            log_request(request, 200, f"Successful login for user {user.phone}")
            return redirect('about')
        else:
            error_message = "Неверный логин или пароль."
            logger.warning(f"Неудачная попытка входа для пользователя: {username}")
            log_request(request, 401, f"Failed login attempt for {username}")

    return render(request, 'html/login.html', {'error_message': error_message})


@login_required
def logout_view(request):
    user_info = f"{request.user.phone} (ID: {request.user.id})"
    logout(request)
    logger.info(f"Пользователь вышел из системы: {user_info}")
    log_request(request, 200, f"User logout: {user_info}")
    return redirect('login')


@login_required
def about_view(request):
    return render(request, 'html/about.html')


@login_required
def index(request):
    return render(request, 'html/index.html')


@login_required
def faq(request):
    return render(request, 'html/a_faq.html')


@login_required
def settings_rules(request):
    if request.method == 'POST':
        form = ServiceForm(user=request.user, data=request.POST)

        if form.is_valid():
            logger.info(f"Форма создания правила прошла валидацию для пользователя {request.user.phone}")
            # Проверяем, установлен ли флаг "Любой отправитель"
            any_sender = form.cleaned_data.get('any_sender', False)
            if any_sender:  # Если флаг установлен
                sender = 'Любой отправитель'
            else:
                sender = form.cleaned_data['sender']

            telephone = form.cleaned_data['telephone']
            telegram_chat = form.cleaned_data['telegram_chat']

            # Создаем правило с учетом флага
            rule = Rules.objects.create(
                user=request.user,
                sender=sender,
                from_whom=telephone,
                to_whom=telegram_chat
            )
            
            logger.info(f"Создано новое правило (ID: {rule.id}) для пользователя {request.user.phone}: {sender} -> {telegram_chat.title}")
            log_request(request, 200, f"Rule created: {sender} -> {telegram_chat.title}")

            return redirect('settings_rules')

        else:
            # Выводим ошибки, если форма невалидна
            logger.warning(f"Ошибки в форме создания правила для пользователя {request.user.phone}: {form.errors}")
            log_request(request, 400, f"Form validation errors: {form.errors}")

    else:
        form = ServiceForm(user=request.user)

    # Получаем все правила для текущего пользователя
    user_rules = Rules.objects.filter(user=request.user)

    return render(request, 'html/a_my_forms.html', {'form': form, 'user_rules': user_rules})


@login_required
def delete_rule(request, rule_id):
    # Получаем объект по его ID
    rule = get_object_or_404(Rules, id=rule_id, user=request.user)

    # Удаляем объект
    if request.method == 'POST':
        rule_info = f"Rule ID: {rule.id}, Sender: {rule.sender}, From: {rule.from_whom.telephone}"
        rule.delete()
        logger.info(f"Пользователь {request.user.phone} удалил правило: {rule_info}")
        log_request(request, 200, f"Rule deleted: {rule_info}")
        return redirect('settings_rules')  # Перенаправляем обратно на страницу настроек

    # Если метод не POST, то просто показываем страницу с подтверждением
    return render(request, 'html/confirm_delete.html', {'rule': rule})


@login_required
def settings_service(request):
    if request.method == 'POST':
        form = ServiceKeyForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            name = form.cleaned_data['name']

            if service == 'Novofon':
                telephone = form.cleaned_data['telephone']
                number_service = NumbersService.objects.create(user=request.user, name=service, telephone=telephone)
                logger.info(f"Пользователь {request.user.phone} добавил номер Novofon: {telephone}")
                log_request(request, 200, f"Novofon number added: {telephone}")
                return JsonResponse({"success": True})
            else:
                key = form.cleaned_data['key']
                api_key = Key.objects.create(user=request.user, name=service, title=name, token=key)
                logger.info(f"Пользователь {request.user.phone} добавил API ключ {service}: {name}")
                log_request(request, 200, f"API key added for {service}: {name}")
                return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = ServiceKeyForm()

    # Получаем все объекты для текущего пользователя
    user_keys = Key.objects.filter(user=request.user)
    user_numbers = NumbersService.objects.filter(user=request.user)

    return render(
        request,
        'html/a_my_input.html',
        {'form': form, 'user_keys': user_keys, 'user_numbers': user_numbers}
    )


@login_required
def delete_number_service(request, id):
    service = get_object_or_404(NumbersService, id=id, user=request.user)
    service_info = f"Service: {service.name}, Phone: {service.telephone}"
    service.delete()
    logger.info(f"Пользователь {request.user.phone} удалил номер сервиса: {service_info}")
    log_request(request, 200, f"Number service deleted: {service_info}")
    return redirect('settings_service')


@login_required
def delete_service(request, key_id):
    key = get_object_or_404(Key, id=key_id, user=request.user)

    if request.method == 'POST':
        key_info = f"Service: {key.name}, Title: {key.title}"
        key.delete()
        logger.info(f"Пользователь {request.user.phone} удалил API ключ: {key_info}")
        log_request(request, 200, f"API key deleted: {key_info}")
        return redirect('settings_service')

    return render(request, 'html/confirm_delete.html', {'key': key})


@csrf_exempt
async def get_webhook(request, token):
    if request.method == 'POST':
        try:
            try:
                user = await sync_to_async(User.objects.get)(token_url=token)
                logger.info(f"Webhook запрос для пользователя: {user.phone} (ID: {user.id})")
            except User.DoesNotExist:
                logger.warning(f"Webhook запрос с неверным токеном: {token[:8]}...")
                return HttpResponseForbidden('Неверный токен')

            data = json.loads(request.body)
            log_webhook_request(token, data, "Processing started")

            if 'result' in data:
                result = data['result']
                caller_did = result.get('caller_did', 'Не указан')
                caller_id = result.get('caller_id', 'Не указан')
                text = result.get('text', 'Не указан')

                logger.info(f"SMS получена: от {caller_id} на {caller_did}, текст: {text[:50]}...")

                rules = await sync_to_async(Rules.objects.filter)(user=user)
                matched_rules = await sync_to_async(
                    lambda: list(rules.filter(sender__in=[caller_id, "Любой отправитель"]))
                )()

                if matched_rules:
                    tg_bot = Bot(settings.TOKEN_BOT)
                    sent_count = 0
                    for rule in matched_rules:
                        try:
                            to_whom_chat_id = await sync_to_async(lambda: rule.to_whom.chat_id)()

                            message_text = (f'Пришло сообщение от {caller_id}\n'
                                            f'На номер: {caller_did}\n'
                                            f'Текст: {text}')
                            await tg_bot.send_message(chat_id=to_whom_chat_id, text=message_text)
                            sent_count += 1
                            logger.info(f"SMS переслана в Telegram канал: {rule.to_whom.title}")
                        except Exception as e:
                            logger.error(f"Ошибка отправки в Telegram канал {rule.to_whom.title}: {e}")

                    processing_result = f"Sent to {sent_count}/{len(matched_rules)} channels"
                    log_webhook_request(token, data, processing_result)
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Данные получены и обработаны',
                        'rules_count': len(matched_rules)
                    }, status=200)
                else:
                    logger.info(f"Для SMS от {caller_id} не найдено подходящих правил")
                    log_webhook_request(token, data, "No matching rules found")
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Данные получены, но правило не найдено'
                    }, status=200)

            else:
                logger.warning(f"Webhook запрос без ключа 'result': {data}")
                log_webhook_request(token, data, "Missing 'result' key")
                return JsonResponse({'status': 'error', 'message': 'Ключ "result" отсутствует'}, status=400)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON в webhook: {e}")
            log_webhook_request(token, {}, f"JSON decode error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON'}, status=400)
        except Exception as e:
            logger.error(f"Критическая ошибка в webhook обработчике: {e}")
            log_webhook_request(token, {}, f"Critical error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500)
    else:
        logger.warning(f"Неподдерживаемый метод {request.method} для webhook")
        return JsonResponse({'status': 'error', 'message': 'Только POST-запросы поддерживаются'}, status=405)
