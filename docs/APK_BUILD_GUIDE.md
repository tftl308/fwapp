# Инструкция по сборке нативного APK для Android (Capacitor)
**Проект: «Огненный Ветер» v4.0.0**

---

## 1. Подготовка окружения на компьютере (однократно)

Для сборки готового бинарного файла `.apk` требуется Android SDK:
1. Установите **Node.js** (версия 18 или новее).
2. Установите **Android Studio** (скачать с официального сайта: developer.android.com).
3. В Android Studio откройте **SDK Manager** и убедитесь, что установлены:
   - Android SDK Platform 33 или 34;
   - Android SDK Build-Tools;
   - Android SDK Command-line Tools.

---

## 2. Сборка APK в 3 команды

В корневой папке проекта выполните:

```bash
# 1. Генерация релизного бандла веб-ядра
npm run build

# 2. Инициализация и синхронизация Capacitor
npx cap add android    # (только при первом запуске)
npx cap sync android   # переносит www/ в нативный проект

# 3. Открытие в Android Studio или сборка через командную строку
npx cap open android
```

### Сборка напрямую без открытия интерфейса Android Studio (CLI):
```bash
cd capacitor-app/android
./gradlew assembleDebug
```
Готовый установочный APK появится по пути:
👉 `capacitor-app/android/app/build/outputs/apk/debug/app-debug.apk`

---

## 3. Настройка прав в `AndroidManifest.xml` (уже преднастроено)
В нативном проекте `capacitor-app/android/app/src/main/AndroidManifest.xml` уже прописаны:
- `WAKE_LOCK` — экран не гаснет во время выступления на сцене;
- `FOREGROUND_SERVICE_MEDIA_PLAYBACK` — воспроизведение фонограмм не прерывается при блокировке экрана;
- `usesCleartextTraffic="true"` — подключение к локальному Wi-Fi серверу на репетиции по протоколу HTTP (`http://192.168.x.x:8080`).
