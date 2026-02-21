# Loki-Grafana
 Loki + Grafana в одном docker-compose на сервере.
 Loki как Data Source в Grafana 
 отправляет логи напрямую в Loki через HTTP POST на эндпоинт /loki/api/v1/push (без Promtail)
