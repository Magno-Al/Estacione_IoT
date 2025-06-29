# To run flutter app local:

## 1. Mongo + API
docker-compose up -d


## 2. Espelha porta no Android (caso não funcione faça o passo 4)
adb reverse tcp:3000 tcp:3000


## 3. No App em Flutter
flutter pub get
flutter run


## 4. Erro ADB
O adb vem por padrão junto com o Android Studio na pasta platform-tools

Exemplo:
C:\Users\USER_NAME\AppData\Local\Android\Sdk\platform-tools

Verifique se existe o adb.exe, se existir adicione o caminho como no exemplo acima nas variáveis de ambiente (no Path)

Depois disso execute: "adb devices" para listar os dispositivos conectados, se aparecer "unauthorized" habilite as opções de desenvolvedor do seu celular e ative a "Deputação Usb" quando aparecer um Pop up permita sempre desse dispositivo

Se o popup não aparecer tente tirar o cabo e conectar de novo ou executar:
adb kill-server
adb start-server

Depois do dispositivo se conectar, volte ao Passo 2
