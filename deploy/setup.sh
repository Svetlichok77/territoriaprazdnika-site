#!/usr/bin/env bash
# Установка сайта territoriaprazdnika.ru рядом с n8n. Запускать от root.
set -e
REPO=https://github.com/Svetlichok77/territoriaprazdnika-site.git

command -v git >/dev/null || { apt-get update -q && apt-get install -y -q git; }

mkdir -p /opt/site
if [ -d /opt/site/repo/.git ]; then
  git -C /opt/site/repo pull -q
else
  git clone -q "$REPO" /opt/site/repo
fi

docker compose -p site -f /opt/site/repo/deploy/docker-compose.yml up -d
docker exec territoriaprazdnika-site nginx -s reload >/dev/null 2>&1 || true

# Автообновление: каждые 5 минут забираем свежую версию из GitHub
CRON='*/5 * * * * git -C /opt/site/repo pull -q >/dev/null 2>&1; docker exec territoriaprazdnika-site nginx -s reload >/dev/null 2>&1'
( crontab -l 2>/dev/null | grep -v '/opt/site/repo pull' ; echo "$CRON" ) | crontab -

echo
echo "ГОТОВО: сайт запущен."
docker ps --format "{{.Names}} | {{.Status}}" | grep territoriaprazdnika
