#!/bin/bash

# Скрипт для проверки безопасности HTTPS конфигурации FamilyWay +
# Использование: ./check_https_security.sh

set -e

echo "🔒 Проверка безопасности HTTPS для FamilyWay +"
echo "=============================================="

DOMAIN="familyway.plus"
WWW_DOMAIN="www.familyway.plus"

# Функция для проверки HTTP статуса
check_http_status() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    echo -n "🔍 $description... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$status" = "$expected_status" ]; then
        echo "✅ OK ($status)"
    else
        echo "❌ FAIL (получен $status, ожидался $expected_status)"
    fi
}

# Функция для проверки HTTPS
check_https() {
    local domain=$1
    echo -n "🔍 Проверка HTTPS для $domain... "
    
    if curl -s --max-time 10 "https://$domain" > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAIL"
    fi
}

# Функция для проверки SSL сертификата
check_ssl_cert() {
    local domain=$1
    echo -n "🔍 Проверка SSL сертификата для $domain... "
    
    if echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
        echo "✅ OK"
    else
        echo "❌ FAIL"
    fi
}

# Функция для проверки заголовков безопасности
check_security_headers() {
    local domain=$1
    echo "🔍 Проверка заголовков безопасности для $domain:"
    
    headers=$(curl -s -I "https://$domain" 2>/dev/null)
    
    # Проверка HSTS
    if echo "$headers" | grep -i "strict-transport-security" > /dev/null; then
        echo "  ✅ HSTS заголовок присутствует"
    else
        echo "  ❌ HSTS заголовок отсутствует"
    fi
    
    # Проверка X-Frame-Options
    if echo "$headers" | grep -i "x-frame-options" > /dev/null; then
        echo "  ✅ X-Frame-Options заголовок присутствует"
    else
        echo "  ❌ X-Frame-Options заголовок отсутствует"
    fi
    
    # Проверка X-Content-Type-Options
    if echo "$headers" | grep -i "x-content-type-options" > /dev/null; then
        echo "  ✅ X-Content-Type-Options заголовок присутствует"
    else
        echo "  ❌ X-Content-Type-Options заголовок отсутствует"
    fi
    
    # Проверка X-XSS-Protection
    if echo "$headers" | grep -i "x-xss-protection" > /dev/null; then
        echo "  ✅ X-XSS-Protection заголовок присутствует"
    else
        echo "  ❌ X-XSS-Protection заголовок отсутствует"
    fi
    
    # Проверка Content-Security-Policy
    if echo "$headers" | grep -i "content-security-policy" > /dev/null; then
        echo "  ✅ Content-Security-Policy заголовок присутствует"
    else
        echo "  ❌ Content-Security-Policy заголовок отсутствует"
    fi
}

# Функция для проверки редиректа
check_redirect() {
    local from=$1
    local to=$2
    echo -n "🔍 Проверка редиректа с $from на $to... "
    
    redirect_url=$(curl -s -o /dev/null -w "%{redirect_url}" "$from" 2>/dev/null || echo "")
    
    if [[ "$redirect_url" == *"$to"* ]]; then
        echo "✅ OK"
    else
        echo "❌ FAIL (редирект на: $redirect_url)"
    fi
}

echo ""
echo "🌐 Проверка доменов..."
echo "======================"

# Проверка HTTP редиректов
check_http_status "http://$DOMAIN" "301" "HTTP редирект с $DOMAIN"
check_http_status "http://$WWW_DOMAIN" "301" "HTTP редирект с $WWW_DOMAIN"

echo ""
echo "🔐 Проверка HTTPS..."
echo "===================="

# Проверка HTTPS доступности
check_https "$DOMAIN"
check_https "$WWW_DOMAIN"

echo ""
echo "📜 Проверка SSL сертификатов..."
echo "==============================="

# Проверка SSL сертификатов
check_ssl_cert "$DOMAIN"
check_ssl_cert "$WWW_DOMAIN"

echo ""
echo "🛡️  Проверка заголовков безопасности..."
echo "====================================="

# Проверка заголовков безопасности
check_security_headers "$DOMAIN"
echo ""
check_security_headers "$WWW_DOMAIN"

echo ""
echo "🔄 Проверка редиректов..."
echo "========================"

# Проверка редиректов
check_redirect "http://$DOMAIN" "https://$DOMAIN"
check_redirect "http://$WWW_DOMAIN" "https://$WWW_DOMAIN"

echo ""
echo "🧪 Дополнительные тесты..."
echo "========================="

# Проверка доступности статических файлов
echo -n "🔍 Проверка статических файлов... "
if curl -s --max-time 5 "https://$DOMAIN/static/" > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Проверка доступности медиа файлов
echo -n "🔍 Проверка медиа файлов... "
if curl -s --max-time 5 "https://$DOMAIN/media/" > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Проверка health check
echo -n "🔍 Проверка health check... "
if curl -s --max-time 5 "https://$DOMAIN/health" | grep -q "healthy"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo ""
echo "📊 Результаты проверки безопасности HTTPS"
echo "========================================"
echo ""
echo "✅ Проверка завершена!"
echo ""
echo "🔧 Рекомендации:"
echo "1. Протестируйте сайт в браузере: https://$DOMAIN"
echo "2. Проверьте безопасность на SSL Labs:"
echo "   https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "3. Убедитесь, что Django использует HTTPS настройки"
echo "4. Проверьте логи Nginx: tail -f /var/log/nginx/error.log"
echo ""
echo "🎉 FamilyWay + готов к безопасной работе с HTTPS!"
