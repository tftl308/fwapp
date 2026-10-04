# Сборка APK на Windows 10 / 11 (Capacitor Native)
**Руководство для музыкантов и администратора проекта «Огненный Ветер» v4.0.0**

---

## 1. Подготовка окружения на Windows (выполняется один раз)

1. **Установите Node.js (LTS)**:
   - Скачайте с официального сайта: [nodejs.org](https://nodejs.org/) (версия 20 LTS).
   - При установке оставьте галочку "Add to PATH".
2. **Установите Android Studio**:
   - Скачайте с официального сайта: [developer.android.com/studio](https://developer.android.com/studio).
   - Запустите стандартную установку.
   - Откройте Android Studio ➔ **More Actions** ➔ **SDK Manager**:
     - Во вкладке **SDK Platforms** выберите **Android 13.0 (Tiramisu)** или **Android 14.0**;
     - Во вкладке **SDK Tools** отметьте:
       - `Android SDK Build-Tools`
       - `Android SDK Command-line Tools`
       - `Android Emulator`
       - `Android SDK Platform-Tools`.
     - Нажмите **Apply** и дождитесь окончания загрузки.

---

## 2. Сборка APK проекта на Windows

Откройте командную строку PowerShell или CMD в папке проекта:

```powershell
# 1. Полная сборка веб-ядра и манифеста
npm run build

# 2. Инициализация платформы Android (только при первом запуске)
npx cap add android

# 3. Синхронизация веб-ядра www/ с нативным проектом
npx cap sync android

# 4. Открытие проекта в Android Studio для сборки
npx cap open android
```

В открывшемся окне Android Studio:
1. Дождитесь завершения автоматической синхронизации Gradle (внизу появится надпись "Gradle sync finished").
2. В верхнем меню выберите: **Build ➔ Build Bundle(s) / APK(s) ➔ Build APK(s)**.
3. Через 1–2 минуты появится уведомление в правом нижнем углу: *"APK(s) generated successfully"*. Нажмите на ссылку **locate**.
4. Готовый файл **`app-debug.apk`** откроется в Проводнике Windows!

---

## 3. Сборка без открытия интерфейса Android Studio (через терминал)

В PowerShell в папке проекта:
```powershell
cd capacitor-app/android
.\gradlew.bat assembleDebug
```
Файл APK появится по адресу:
👉 `capacitor-app\android\app\build\outputs\apk\debug\app-debug.apk`
