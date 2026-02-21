#!/usr/bin/env python3
"""
CryptoExchange Backend — эмуляция работы криптовалютной биржи.
Генерирует непрерывный поток событий в виде простых текстовых логов.
"""

import requests
import random
import time
import json

LOKI_URL = "http://localhost:3100/loki/api/v1/push"

COINS = {
    "BTC":  67_432.18,
    "ETH":  3_521.44,
    "SOL":  172.63,
    "XRP":  0.62,
    "DOGE": 0.15,
    "ADA":  0.58,
    "AVAX": 38.90,
    "DOT":  7.84,
    "BNB":  587.30,
    "MATIC": 0.91,
    "LINK": 18.42,
}

USERS = [
    "mining_pool", "defi_master", "hodler_2024", "crypto_trader_1",
    "nft_collector", "whale_alert", "satoshi_fan", "block_miner",
    "token_sniper", "yield_farmer", "dao_voter", "flash_loan_bot",
    "arb_hunter", "staking_pro", "swap_king",
]

ACTIONS = ["buy", "sell", "transfer"]


def send_log_to_loki(message, job="crypto-exchange", level="INFO"):
    """Отправляет лог в Loki"""
    timestamp = str(int(time.time() * 1000000000))

    payload = {
        "streams": [
            {
                "stream": {
                    "job": job,
                    "level": level,
                },
                "values": [[timestamp, message]],
            }
        ]
    }

    try:
        response = requests.post(LOKI_URL, json=payload)
        if response.status_code == 204:
            print(f"✓ Лог отправлен: {message}")
        else:
            print(f"✗ Ошибка отправки: {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")


def jitter(price):
    """Случайное отклонение цены."""
    return round(price * random.uniform(0.95, 1.05), 2)


def update_prices():
    """Сдвигает цены всех монет."""
    for coin in COINS:
        COINS[coin] = round(COINS[coin] * (1 + random.uniform(-0.003, 0.003)), 6)


def trade_event():
    """Сделка: покупка / продажа / перевод."""
    user = random.choice(USERS)
    coin = random.choice(list(COINS.keys()))
    action = random.choice(ACTIONS)
    amount = round(random.uniform(0.01, 10.0), 6)
    price = jitter(COINS[coin])

    success = random.random() > 0.15

    if success:
        msg = f"Транзакция выполнена: {user} {action} {amount} {coin} по цене ${price}"
        send_log_to_loki(msg, level="INFO")
    else:
        msg = f"Ошибка транзакции: {user} - {action} {amount} {coin}"
        send_log_to_loki(msg, level="ERROR")


def deposit_withdrawal():
    """Депозит или вывод."""
    user = random.choice(USERS)
    coin = random.choice(list(COINS.keys()))
    direction = random.choice(["deposit", "withdrawal"])
    amount = round(random.uniform(0.05, 8.0), 6)
    price = jitter(COINS[coin])
    usd = round(amount * price, 2)

    if direction == "deposit":
        msg = f"Депозит: {user} внёс {amount} {coin} (${usd})"
    else:
        msg = f"Вывод средств: {user} вывел {amount} {coin} (${usd})"

    send_log_to_loki(msg, level="INFO")


def order_event():
    """Размещение ордера."""
    user = random.choice(USERS)
    coin = random.choice(list(COINS.keys()))
    side = random.choice(["buy", "sell"])
    order_type = random.choice(["market", "limit", "stop-loss"])
    amount = round(random.uniform(0.01, 5.0), 6)
    price = jitter(COINS[coin])

    msg = f"Ордер {order_type}: {user} {side} {amount} {coin} по цене ${price}"
    send_log_to_loki(msg, level="INFO")


def auth_event():
    """Авторизация."""
    user = random.choice(USERS)
    success = random.random() > 0.1

    if success:
        msg = f"Авторизация: {user} вошёл в систему"
        send_log_to_loki(msg, level="INFO")
    else:
        reason = random.choice(["неверный пароль", "истёк 2FA", "IP заблокирован", "аккаунт заморожен"])
        msg = f"Ошибка авторизации: {user} - {reason}"
        send_log_to_loki(msg, level="WARN")


def price_alert():
    """Алерт по цене."""
    coin = random.choice(list(COINS.keys()))
    price = COINS[coin]
    change = round(random.uniform(-5.0, 5.0), 2)
    direction = "вырос" if change > 0 else "упал"

    msg = f"Алерт: {coin} {direction} на {abs(change)}%, текущая цена ${round(price, 2)}"
    send_log_to_loki(msg, level="WARN")


def whale_move():
    """Крупная транзакция."""
    user = random.choice(USERS)
    coin = random.choice(["BTC", "ETH", "BNB"])
    amount = round(random.uniform(50, 500), 2)
    price = COINS[coin]
    usd = round(amount * price, 2)

    msg = f"Крупная транзакция: {user} перевёл {amount} {coin} (${usd})"
    send_log_to_loki(msg, level="WARN")


def system_event():
    """Системное событие."""
    events = [
        "Система: проверка healthcheck — OK",
        f"Система: активных подключений WebSocket — {random.randint(500, 15000)}",
        f"Система: API запросов в секунду — {random.randint(200, 8000)}",
        f"Система: CPU {round(random.uniform(10, 85), 1)}%, RAM {round(random.uniform(20, 70), 1)}%",
        f"Система: обработано ордеров за минуту — {random.randint(100, 5000)}",
    ]
    msg = random.choice(events)
    send_log_to_loki(msg, level="INFO")


# ── Главный цикл ────────────────────────────────────────────────────

EVENTS = [
    (trade_event,         35),
    (order_event,         20),
    (deposit_withdrawal,  15),
    (auth_event,          10),
    (price_alert,         10),
    (system_event,         5),
    (whale_move,           5),
]

EVENT_FNS = []
for fn, weight in EVENTS:
    EVENT_FNS.extend([fn] * weight)


def main():
    send_log_to_loki("CryptoExchange Backend запущен", level="INFO")

    while True:
        update_prices()
        fn = random.choice(EVENT_FNS)
        fn()
        time.sleep(random.uniform(0.15, 1.2))


if __name__ == "__main__":
    main()
