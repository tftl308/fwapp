# Сборка APK на Альт Образование 10.4 (ALT Linux p10)
**Специализированное руководство для сборки мобильного приложения «Огненный Ветер» v4.0.0**

---

## 1. Особенности дистрибутива Альт Образование 10.4
- Пакетный менеджер: **`apt-get`** / **`epm`** (через утилиту `eepm`);
- Базовая ветка репозиториев: **p10**;
- Архитектура: `x86_64`.

---

## 2. Пошаговая установка необходимых пакетов

Откройте терминал и выполните команды от имени администратора (`su -` или через `sudo`):

### Шаг 2.1: Установка JDK и базовых утилит
В Альт Linux 10.4 для Android SDK рекомендуется **Java 17**:
```bash
su -
apt-get update
apt-get install -y java-17-openjdk java-17-openjdk-devel git curl unzip
exit
```
Проверьте версию Java:
```bash
java -version
# Должно вывести OpenJDK Runtime Environment (build 17.x.x)
```

### Шаг 2.2: Установка Node.js (18 или 20)
Если Node.js ещё не установлен:
```bash
su -
apt-get install -y node node-devel npm
exit
```

---

## 3. Установка Android Command-Line Tools (SDK) на Альт Linux

Для сборки APK без графической среды Android Studio достаточно официальных консольных утилит:

```bash
# 1. Создаем папку для Android SDK в домашней директории
mkdir -p ~/android-sdk/cmdline-tools

# 2. Скачиваем официальные commandlinetools для Linux
cd ~/Downloads
curl -O https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip

# 3. Распаковываем в правильную иерархию (latest)
unzip commandlinetools-linux-*.zip
mkdir -p ~/android-sdk/cmdline-tools/latest
mv cmdline-tools/* ~/android-sdk/cmdline-tools/latest/ 2>/dev/null || true

# 4. Прописываем переменные окружения в ~/.bashrc
cat << 'ENVEOF' >> ~/.bashrc
export ANDROID_HOME=$HOME/android-sdk
export ANDROID_SDK_ROOT=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
ENVEOF

source ~/.bashrc
```

### Шаг 3.1: Принятие лицензий и установка платформ SDK:
```bash
# Принять лицензии Google
yes | sdkmanager --licenses

# Установить SDK Platform 33/34 и build-tools
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
```

*(Примечание: если вам удобнее работать с графическим интерфейсом, на Альт Образование можно установить **Android Studio** в один клик через `epm play android-studio`)*.

---

## 4. Сборка готового APK проекта

В папке проекта «Огненный Ветер»:

```bash
# 1. Полная сборка веб-ядра и манифеста
npm run build

# 2. Инициализация и синхронизация Capacitor
npx cap add android    # выполняется один раз
npx cap sync android   # переносит собранные файлы www/

# 3. Сборка APK с помощью Gradle
cd capacitor-app/android
./gradlew assembleDebug
```

Готовый файл APK будет лежать здесь:
👉 **`capacitor-app/android/app/build/outputs/apk/debug/app-debug.apk`**

Его можно сразу скинуть на флешку или передать по Telegram/сети на телефоны музыкантов группы!
