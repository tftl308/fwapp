#!/usr/bin/env python3
"""
Локальный сервер «Огненный Ветер» для локальной раздачи и PWA-установки
Поддерживает аргумент: --serve-files (раздача полной медиатеки music/ и манифеста)
"""
import http.server
import socketserver
import socket
import os
import sys

DEFAULT_PORT = 8080

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Разрешаем Service Worker, кросс-доменные запросы и потоковое воспроизведение Range
        self.send_header('Service-Worker-Allowed', '/')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Range, Content-Type')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

if __name__ == '__main__':
    port = DEFAULT_PORT
    serve_files = False

    for arg in sys.argv[1:]:
        if arg == '--serve-files':
            serve_files = True
        elif arg.isdigit():
            port = int(arg)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    local_ip = get_local_ip()

    with socketserver.TCPServer(('0.0.0.0', port), CustomHandler) as httpd:
        print("=" * 65)
        print("🔥 ЛОКАЛЬНЫЙ PWA & МЕДИА-СЕРВЕР «ОГНЕННЫЙ ВЕТЕР» v4.0.0 ЗАПУЩЕН!")
        print("=" * 65)
        print(f"1. Локально на компьютере:    http://localhost:{port}")
        print(f"2. НА СМАРТФОНЕ / ПЛАНШЕТЕ:   http://{local_ip}:{port}")
        if serve_files:
            print("📁 Режим --serve-files:      Раздача фонограмм music/ и манифеста активна")
        print("-" * 65)
        print("💡 ДЛЯ МУЗЫКАНТОВ:")
        print(f"   Откройте Chrome/Safari: http://{local_ip}:{port}")
        print("   Нажмите: «Установить приложение» / «На экран Домой»")
        print("   Приложение скачает актуальный каталог и будет работать без сети!")
        print("=" * 65)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
