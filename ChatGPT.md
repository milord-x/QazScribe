Есть проект который я брался за 100тысач тенге, срок два дня.
Надо поднять сервер сайт. Для мобилку и на десктоп.

Сайт для универа, он переводит речи в конспект и кратки резюме, используется для заседаний, конференций и тд. Она сказала что в конференциях говорится очен много инфы и на разных языках, надо собрать программу для этого.

Принимает онлайн и фалы речи
Обравабывает: Аудио конференции →
распознавание речи → текст →
перевод на казахский →
структурирование готовый документ

Я хочу создать проект и когда он будет готов подключить его к их серверу и завершит работу. У них не сервер а пк с ubuntu.

Им нужна чтобы через сайт они могли выполнит свои действие а бэкенд будет убунту

Понятно?
Есть уточнение?
aidana@aidana-Predator:~$ inxi -Fz
System:
  Kernel: 6.11.0-26-generic arch: x86_64 bits: 64
  Desktop: GNOME v: 46.0 Distro: Ubuntu 24.04.1 LTS (Noble Numbat)
Machine:
  Type: Desktop Mobo: Acer model: Predator POX-650 v: 1.0
    serial: <superuser required> UEFI: American Megatrends v: 1.02
    date: 09/11/2023
CPU:
  Info: 10-core (6-mt/4-st) model: 13th Gen Intel Core i5-13400F bits: 64
    type: MST AMCP cache: L2: 9.5 MiB
  Speed (MHz): avg: 907 min/max: 800/4600:3300 cores: 1: 900 2: 800 3: 800
    4: 800 5: 892 6: 928 7: 900 8: 938 9: 934 10: 936 11: 950 12: 928 13: 960
    14: 1023 15: 916 16: 917
Graphics:
  Device-1: NVIDIA AD104 [GeForce RTX 4070 Ti] driver: nvidia v: 535.230.02
  Display: x11 server: X.Org v: 21.1.11 with: Xwayland v: 23.2.6 driver: X:
    loaded: nouveau unloaded: fbdev,modesetting,vesa dri: swrast
    gpu: nvidia,nvidia-nvswitch resolution: 1920x1080~60Hz
  API: EGL v: 1.5 drivers: swrast platforms: x11,surfaceless,device
  API: OpenGL v: 4.5 vendor: mesa v: 24.2.8-1ubuntu1~24.04.1
    renderer: llvmpipe (LLVM 19.1.1 256 bits)
Audio:
  Device-1: Intel Raptor Lake High Definition Audio driver: snd_hda_intel
  Device-2: NVIDIA driver: snd_hda_intel
  API: ALSA v: k6.11.0-26-generic status: kernel-api
  Server-1: PipeWire v: 1.0.5 status: active
Network:
  Device-1: Intel Raptor Lake-S PCH CNVi WiFi driver: iwlwifi
  IF: wlp0s20f3 state: up mac: <filter>
  Device-2: Realtek Killer E3000 2.5GbE driver: r8169
  IF: enp3s0 state: up speed: 100 Mbps duplex: full mac: <filter>
Bluetooth:
  Device-1: Intel AX211 Bluetooth driver: btusb type: USB
  Report: hciconfig ID: hci0 rfk-id: 0 state: down
    bt-service: enabled,running rfk-block: hardware: no software: yes
    address: <filter>
Drives:
  Local Storage: total: 953.87 GiB used: 266.11 GiB (27.9%)
  ID-1: /dev/nvme0n1 vendor: Micron model: 2450 MTFDKBA1T0TFK
    size: 953.87 GiB
Partition:
  ID-1: / size: 296.01 GiB used: 266.05 GiB (89.9%) fs: ext4
    dev: /dev/nvme0n1p5
  ID-2: /boot/efi size: 256 MiB used: 62 MiB (24.2%) fs: vfat
    dev: /dev/nvme0n1p1
Swap:
  ID-1: swap-1 type: file size: 4 GiB used: 0 KiB (0.0%) file: /swap.img
Sensors:
  System Temperatures: cpu: 47.0 C mobo: N/A
  Fan Speeds (rpm): N/A
Info:
  Memory: total: 16 GiB note: est. available: 15.37 GiB used: 2.82 GiB (18.4%)
  Processes: 380 Uptime: 20m Shell: Bash inxi: 3.3.34


2. Формат работы
Они хочет оба вариянта, реалный речевой контекст и когда не доступна сайт и на аудио файлы

Важно тюркоязычные языки и англиский, они удивилис с wisper и хочет с перва добавит его. А потом когда программу можно показать сделать чтобы можно добавит еще несколько агентов для важности программы а так на основном виспер

4. Финальный документ
Да 4 формата надо им

5 нет не нужна авторизация

Нет не надо хранит данные они должны остатся в сервере и ощищатся


Теперь точно понял ситуацию?

Мы создадим гитхаб репо и каждый код и каждый менялку там пушим всегда потом когда закончим проект скачаем его в убунту и настроим и поставим
Нам надо публичный сервер локльного не удобен
Смотри если конференция в другом конце города и там же локаль не будет
Так что нам надо определит как будет сайт

Повторно спросил им нужен сохранение данных но у убунту внутри свободно только 16гб памяти для проекта и говорит 16гб озу есть
Надо сделать хранение данных таким типа по истечению времени данные автоматический очищается и освободять месту.

Этот проект вручена одному учителю который он должен был сделать и дедлайны его подходят и ему просто надо показать как работает все далнейшие использование не усмотрено по моему, я так замечал
Давай пиши все все все о проекте к агенту не важно кодекс или клод
Он создал проект внутри ~/Projects
Соеденил с гитхаб 

Я буду в основном кодит на своем ноуте перекидывая все работы на гитхаб, не хочу на самом сранном убунту работат.

Когда соберем первый рабочий протоип с не  лучший сайтом настройм сам убунту там с ртикс и поставим там первый протоип там будем тестировать

Кароче понятно?
Ой ой можеш все это собрать в markdown файлу?
предложи один очень сильный название для проекта
коротко