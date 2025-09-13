# 🔒 Руководство по настройке HTTPS для FamilyWay +

## 🚀 Быстрая настройка

### 1. Автоматическая настройка (рекомендуется)
```bash
# Запустите автоматический скрипт
sudo ./setup_ssl.sh
```

### 2. Проверка безопасности
```bash
# Проверьте настройки HTTPS
./check_https_security.sh
```

## 📋 Что настроено

### Django настройки (settings_production.py):
- ✅ `SECURE_SSL_REDIRECT = True` - принудительный редирект на HTTPS
- ✅ `SESSION_COOKIE_SECURE = True` - безопасные cookies
- ✅ `CSRF_COOKIE_SECURE = True` - безопасные CSRF токены
- ✅ `SECURE_HSTS_SECONDS = 31536000` - HSTS на 1 год
- ✅ `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` - HSTS для поддоменов
- ✅ `SECURE_HSTS_PRELOAD = True` - предзагрузка HSTS

### Nginx конфигурация:
- ✅ HTTP → HTTPS редирект (301)
- ✅ SSL/TLS 1.2 и 1.3
- ✅ Безопасные SSL шифры
- ✅ SSL stapling
- ✅ Заголовки безопасности:
  - `Strict-Transport-Security`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection`
  - `Content-Security-Policy`
  - `Permissions-Policy`

### Безопасность файлов:
- ✅ Блокировка доступа к `.env`, `.log`, `.sql` файлам
- ✅ Блокировка backup файлов
- ✅ Блокировка версионного контроля (`.git`, `.svn`)

## 🔧 Ручная настройка

### 1. Установка Certbot
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Получение SSL сертификата
```bash
sudo certbot --nginx -d familyway.plus -d www.familyway.plus
```

### 3. Настройка автообновления
```bash
# Добавить в crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo crontab -
```

### 4. Проверка конфигурации
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 🧪 Тестирование

### 1. Проверка редиректов
```bash
# HTTP должен редиректить на HTTPS
curl -I http://familyway.plus
curl -I http://www.familyway.plus
```

### 2. Проверка HTTPS
```bash
# HTTPS должен работать
curl -I https://familyway.plus
curl -I https://www.familyway.plus
```

### 3. Проверка безопасности
- Откройте https://www.ssllabs.com/ssltest/
- Введите ваш домен: `familyway.plus`
- Проверьте оценку безопасности

## 🚨 Важные моменты

### Перед настройкой HTTPS:
1. ✅ Убедитесь, что домен указывает на ваш сервер
2. ✅ Откройте порты 80 и 443 в файрволе
3. ✅ Остановите другие веб-серверы на портах 80/443

### После настройки HTTPS:
1. ✅ Проверьте работу сайта в браузере
2. ✅ Убедитесь, что Django использует HTTPS настройки
3. ✅ Проверьте логи: `tail -f /var/log/nginx/error.log`

## 🔍 Диагностика проблем

### Проблема: "SSL certificate not found"
```bash
# Проверьте сертификаты
sudo certbot certificates

# Обновите сертификат
sudo certbot renew --force-renewal
```

### Проблема: "Nginx configuration error"
```bash
# Проверьте синтаксис
sudo nginx -t

# Перезагрузите конфигурацию
sudo systemctl reload nginx
```

### Проблема: "Django not using HTTPS"
```bash
# Убедитесь, что используете production настройки
export DJANGO_SETTINGS_MODULE=baybyway.settings_production
python manage.py runserver
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `sudo journalctl -u nginx -f`
2. Запустите диагностику: `./check_https_security.sh`
3. Проверьте статус сертификатов: `sudo certbot certificates`

---

**🎉 Поздравляем! FamilyWay + теперь работает с максимальной безопасностью HTTPS!**
