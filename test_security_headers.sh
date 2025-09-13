#!/bin/bash

# Скрипт для тестирования заголовков безопасности FamilyWay +
# Использование: ./test_security_headers.sh

set -e

echo "🛡️  Тестирование заголовков безопасности FamilyWay +"
echo "=================================================="

DOMAIN="familyway.plus"
WWW_DOMAIN="www.familyway.plus"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для проверки заголовка
check_header() {
    local domain=$1
    local header_name=$2
    local expected_value=$3
    local description=$4
    
    echo -n "🔍 $description... "
    
    # Получаем заголовки
    headers=$(curl -s -I "https://$domain" 2>/dev/null || echo "")
    
    if [ -z "$headers" ]; then
        echo -e "${RED}❌ FAIL (не удалось получить ответ)${NC}"
        return 1
    fi
    
    # Ищем заголовок (case insensitive)
    header_line=$(echo "$headers" | grep -i "^$header_name:" || echo "")
    
    if [ -z "$header_line" ]; then
        echo -e "${RED}❌ FAIL (заголовок отсутствует)${NC}"
        return 1
    fi
    
    # Проверяем значение (если указано)
    if [ -n "$expected_value" ]; then
        if echo "$header_line" | grep -qi "$expected_value"; then
            echo -e "${GREEN}✅ OK${NC}"
            echo "   📋 Значение: $header_line"
        else
            echo -e "${YELLOW}⚠️  WARNING (неожиданное значение)${NC}"
            echo "   📋 Ожидалось: $expected_value"
            echo "   📋 Получено: $header_line"
        fi
    else
        echo -e "${GREEN}✅ OK${NC}"
        echo "   📋 Значение: $header_line"
    fi
    
    return 0
}

# Функция для проверки SSL
check_ssl() {
    local domain=$1
    echo -n "🔍 Проверка SSL для $domain... "
    
    if echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
        
        # Получаем информацию о сертификате
        cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | openssl x509 -noout -text 2>/dev/null)
        
        # Проверяем протокол
        protocol=$(echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | grep "Protocol" || echo "")
        if [ -n "$protocol" ]; then
            echo "   📋 $protocol"
        fi
        
        # Проверяем шифр
        cipher=$(echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | grep "Cipher" || echo "")
        if [ -n "$cipher" ]; then
            echo "   📋 $cipher"
        fi
        
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Функция для проверки редиректа
check_redirect() {
    local from=$1
    local to=$2
    echo -n "🔍 Проверка редиректа с $from на $to... "
    
    redirect_url=$(curl -s -o /dev/null -w "%{redirect_url}" "$from" 2>/dev/null || echo "")
    
    if [[ "$redirect_url" == *"$to"* ]]; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "   📋 Редирект на: $redirect_url"
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "   📋 Ожидался редирект на: $to"
        echo "   📋 Получен редирект на: $redirect_url"
        return 1
    fi
}

echo ""
echo "🌐 Проверка доменов..."
echo "======================"

# Проверка HTTP редиректов
check_redirect "http://$DOMAIN" "https://$DOMAIN"
check_redirect "http://$WWW_DOMAIN" "https://$WWW_DOMAIN"

echo ""
echo "🔐 Проверка SSL..."
echo "=================="

# Проверка SSL
check_ssl "$DOMAIN"
echo ""
check_ssl "$WWW_DOMAIN"

echo ""
echo "🛡️  Проверка заголовков безопасности..."
echo "====================================="

# Проверка основных заголовков безопасности
check_header "$DOMAIN" "Strict-Transport-Security" "max-age=31536000" "HSTS заголовок"
check_header "$DOMAIN" "X-Frame-Options" "DENY" "X-Frame-Options заголовок"
check_header "$DOMAIN" "X-Content-Type-Options" "nosniff" "X-Content-Type-Options заголовок"
check_header "$DOMAIN" "X-XSS-Protection" "1; mode=block" "X-XSS-Protection заголовок"
check_header "$DOMAIN" "Referrer-Policy" "strict-origin-when-cross-origin" "Referrer-Policy заголовок"
check_header "$DOMAIN" "Content-Security-Policy" "" "Content-Security-Policy заголовок"
check_header "$DOMAIN" "Permissions-Policy" "" "Permissions-Policy заголовок"

echo ""
echo "🔍 Дополнительные проверки..."
echo "============================="

# Проверка доступности статических файлов
echo -n "🔍 Проверка статических файлов... "
if curl -s --max-time 5 "https://$DOMAIN/static/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (статические файлы недоступны)${NC}"
fi

# Проверка доступности медиа файлов
echo -n "🔍 Проверка медиа файлов... "
if curl -s --max-time 5 "https://$DOMAIN/media/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (медиа файлы недоступны)${NC}"
fi

# Проверка health check
echo -n "🔍 Проверка health check... "
health_response=$(curl -s --max-time 5 "https://$DOMAIN/health" 2>/dev/null || echo "")
if echo "$health_response" | grep -q "healthy"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING (health check недоступен)${NC}"
fi

echo ""
echo "🚫 Проверка блокировки чувствительных файлов..."
echo "============================================="

# Проверка блокировки .env файлов
echo -n "🔍 Проверка блокировки .env файлов... "
env_status=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/.env" 2>/dev/null || echo "000")
if [ "$env_status" = "403" ] || [ "$env_status" = "404" ]; then
    echo -e "${GREEN}✅ OK (заблокирован)${NC}"
else
    echo -e "${RED}❌ FAIL (доступен, код: $env_status)${NC}"
fi

# Проверка блокировки .git файлов
echo -n "🔍 Проверка блокировки .git файлов... "
git_status=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/.git" 2>/dev/null || echo "000")
if [ "$git_status" = "403" ] || [ "$git_status" = "404" ]; then
    echo -e "${GREEN}✅ OK (заблокирован)${NC}"
else
    echo -e "${RED}❌ FAIL (доступен, код: $git_status)${NC}"
fi

# Проверка блокировки backup файлов
echo -n "🔍 Проверка блокировки backup файлов... "
backup_status=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/backup.sql" 2>/dev/null || echo "000")
if [ "$backup_status" = "403" ] || [ "$backup_status" = "404" ]; then
    echo -e "${GREEN}✅ OK (заблокирован)${NC}"
else
    echo -e "${RED}❌ FAIL (доступен, код: $backup_status)${NC}"
fi

echo ""
echo "📊 Сводка результатов..."
echo "======================="

# Подсчет результатов
total_checks=0
passed_checks=0

# Проверяем основные заголовки
headers=("Strict-Transport-Security" "X-Frame-Options" "X-Content-Type-Options" "X-XSS-Protection" "Referrer-Policy" "Content-Security-Policy" "Permissions-Policy")

for header in "${headers[@]}"; do
    total_checks=$((total_checks + 1))
    if curl -s -I "https://$DOMAIN" 2>/dev/null | grep -qi "^$header:"; then
        passed_checks=$((passed_checks + 1))
    fi
done

# Проверяем SSL
total_checks=$((total_checks + 1))
if echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
    passed_checks=$((passed_checks + 1))
fi

# Проверяем редирект
total_checks=$((total_checks + 1))
redirect_url=$(curl -s -o /dev/null -w "%{redirect_url}" "http://$DOMAIN" 2>/dev/null || echo "")
if [[ "$redirect_url" == *"https://$DOMAIN"* ]]; then
    passed_checks=$((passed_checks + 1))
fi

# Вычисляем процент
percentage=$((passed_checks * 100 / total_checks))

echo "📈 Результаты: $passed_checks из $total_checks проверок пройдено ($percentage%)"

if [ $percentage -ge 90 ]; then
    echo -e "${GREEN}🎉 Отличная безопасность! A+ рейтинг${NC}"
elif [ $percentage -ge 80 ]; then
    echo -e "${YELLOW}✅ Хорошая безопасность! A рейтинг${NC}"
elif [ $percentage -ge 70 ]; then
    echo -e "${YELLOW}⚠️  Средняя безопасность! B рейтинг${NC}"
else
    echo -e "${RED}❌ Низкая безопасность! Требуются улучшения${NC}"
fi

echo ""
echo "🔧 Рекомендации:"
echo "1. Проверьте сайт в браузере: https://$DOMAIN"
echo "2. Протестируйте на SSL Labs: https://www.ssllabs.com/ssltest/"
echo "3. Проверьте заголовки на Security Headers: https://securityheaders.com/"
echo "4. Используйте Mozilla Observatory: https://observatory.mozilla.org/"
echo ""
echo "🎉 Тестирование завершено!"
