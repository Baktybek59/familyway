#!/bin/bash

# Скрипт для настройки SSL сертификатов для FamilyWay +
# Использование: sudo ./setup_ssl.sh

set -e

echo "🔒 Настройка SSL сертификатов для FamilyWay +"
echo "=============================================="

# Проверка прав администратора
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: Запустите скрипт с правами администратора (sudo)"
    exit 1
fi

# Переменные
DOMAIN="familyway.plus"
WWW_DOMAIN="www.familyway.plus"
EMAIL="admin@familyway.plus"
NGINX_CONFIG="/etc/nginx/sites-available/familyway.plus"
NGINX_ENABLED="/etc/nginx/sites-enabled/familyway.plus"

echo "📋 Информация о домене:"
echo "   Основной домен: $DOMAIN"
echo "   WWW домен: $WWW_DOMAIN"
echo "   Email: $EMAIL"
echo ""

# Обновление системы
echo "🔄 Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "📦 Установка необходимых пакетов..."
apt install -y nginx certbot python3-certbot-nginx ufw

# Настройка файрвола
echo "🔥 Настройка файрвола..."
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw status

# Остановка Nginx для получения сертификата
echo "⏹️  Остановка Nginx..."
systemctl stop nginx

# Получение SSL сертификата
echo "🔐 Получение SSL сертификата от Let's Encrypt..."
certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN,$WWW_DOMAIN

# Проверка сертификата
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ Ошибка: Не удалось получить SSL сертификат"
    exit 1
fi

echo "✅ SSL сертификат успешно получен"

# Копирование конфигурации Nginx
echo "📝 Настройка конфигурации Nginx..."
cp nginx_baybyway.conf $NGINX_CONFIG

# Создание символической ссылки
ln -sf $NGINX_CONFIG $NGINX_ENABLED

# Удаление дефолтной конфигурации
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации Nginx
echo "🔍 Проверка конфигурации Nginx..."
nginx -t

if [ $? -ne 0 ]; then
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

# Запуск Nginx
echo "🚀 Запуск Nginx..."
systemctl start nginx
systemctl enable nginx

# Настройка автообновления сертификатов
echo "🔄 Настройка автообновления сертификатов..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -

# Проверка статуса
echo "📊 Проверка статуса сервисов..."
systemctl status nginx --no-pager
systemctl status certbot.timer --no-pager

# Тест SSL
echo "🧪 Тестирование SSL..."
echo "Проверка HTTP редиректа:"
curl -I http://$DOMAIN 2>/dev/null | head -1

echo "Проверка HTTPS:"
curl -I https://$DOMAIN 2>/dev/null | head -1

# Проверка безопасности SSL
echo "🔒 Проверка безопасности SSL..."
echo "Тестирование с помощью SSL Labs (запустите в браузере):"
echo "https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"

echo ""
echo "✅ Настройка SSL завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Проверьте работу сайта: https://$DOMAIN"
echo "2. Проверьте редирект с HTTP: http://$DOMAIN"
echo "3. Протестируйте безопасность на SSL Labs"
echo "4. Убедитесь, что Django использует HTTPS настройки"
echo ""
echo "🔧 Полезные команды:"
echo "   Проверка сертификата: certbot certificates"
echo "   Обновление сертификата: certbot renew"
echo "   Перезагрузка Nginx: systemctl reload nginx"
echo "   Логи Nginx: tail -f /var/log/nginx/error.log"
echo ""
echo "🎉 FamilyWay + готов к безопасной работе!"
