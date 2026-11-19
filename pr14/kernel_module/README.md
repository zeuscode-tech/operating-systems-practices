# Учебный модуль ядра

Модуль регистрирует `/dev/pr14demo`, из которого читается строка. Запускайте только в отдельной учебной Ubuntu VM.

```bash
sudo apt install build-essential linux-headers-$(uname -r)
make
sudo insmod mychardev.ko
cat /dev/pr14demo
sudo rmmod mychardev
make clean
```
