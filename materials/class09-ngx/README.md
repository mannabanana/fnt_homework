## Описание

На этом занятии мы поговорили про балансировщики нагрузки и про Ngnx в частности. Узнали, зачем нужны балансировщики нагрузки, какие проблемы решают. Основные различия apache, nginx, haproxy. Также познакомились глубже с Nginx --- как он обрабатывает запросы и примеры конфигурации

## Домашнее задание

### 1. Простой html-сайт

#### Установка nginx

Добавляем Nginx-репозиторий
```bash
$ sudo rpm --import https://nginx.org/keys/nginx_signing.key
$ sudo rm -rf /etc/yum.repos.d/puppet5.repo
$ sudo cat > /etc/yum.repos.d/nginx.repo << 'EOF'
[nginx.org]
name=Nginx official repo (binaries)
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
enabled=1

[nginx.org-src]
name=Nginx official repo (sources)
baseurl=http://nginx.org/packages/centos/7/SRPMS/
enabled=1
EOF

$ sudo yum clean all && yum install -y nginx
```


#### Простой статический сайт

* Стартуем сервис `nginx`
* Включаем старт `nginx` при загрузке ОС
* Добавляем **минимальный** конфиг по пути `/etc/nginx/conf.d/1-test.conf`, со следующими параметрами:
  * имя сервера, на которое откликается сервер: `test-1`
  * порт: `80`
  * корень для сайта: `/var/www/test-1`

```bash
# Разместим тестовую индекс страницу по адресу:
$ cat /var/www/test-1/index.html
Yohoo, it works

# Добавляем прав SELinux на каталоги, ианче у пользователя Nginx Не будет прав читать файлы
sudo chcon -Rt httpd_sys_content_t /var/www

# Перезагружаем nginx, чтобы применить конифгурацию
sudo nginx -s reload

# Сделаем так, чтобы запросы с этой же машины по имени `test-1` и `test-2` приходили на неё же
... (решение описать)

# Проверяем, что всё работает:
$ curl test-1
Yohoo, it works

# Вопрос - почему намш конфиг используется nginx-ом? Как/почему он его подтягивает?

# Тестируем дальше
$ curl test-2
Yohoo, it works
# Ooouch...!
```

* Подправить конфиг `/etc/nginx/conf.d/default.conf` таким образом, чтобы:
  * Он был конфигом по умолчанию (отдавался на все явно не указанные server_name на 80-м порту)
  * Минимальным (убрать из него лишние комментарии и секции)
  * На все запросы отдавался бы код `404` с телом `'No <имя сервера> server config found` (подсказка см. `return`)

Убеждаемся что теперь запрос `curl test-2` не отдаёт нам первый попавшийся сайт.

Выполненные команды и краткие пояснения описать в `README.md`, плюс содержимое конфигов `1-test.conf` и `default.conf`.


### 2. Сборка и запуск Nginx с VTS-модулем

В этой части соберём nginx с модулем для статистики/мониторинга [vts](https://github.com/vozlt/nginx-module-vts), 
чтобы получить как минимум вот такие картинки
![NGINX VTS](https://cloud.githubusercontent.com/assets/3648408/23890539/a4c0de18-08d5-11e7-9a8b-448662454854.png)

Дальнейшие команды важно выполнять не от root, а от своего пользователя

#### Сборка Nginx

* Поключаем репу epel и базовые пакеты сборки `sudo yum install -y epel-release yum-utils rpm-build rpmdevtools`
* Ставим средств разработки `sudo yum groupinstall -y 'Development Tools'`

```bash
# Скачиваем `nginx.src.rpm`
$ cd ~
$ yumdownloader --source nginx
Loaded plugins: fastestmirror
Enabling updates-source repository
Enabling base-source repository
Enabling extras-source repository
base-source                                                                           | 2.9 kB  00:00:00     
extras-source                                                                         | 2.9 kB  00:00:00     
updates-source                                                                        | 2.9 kB  00:00:00     
(1/2): updates-source/7/primary_db                                                              |  77 kB  00:00:00     
(2/2): extras-source/7/primary_db                                                               |  49 kB  00:00:00     
Determining fastest mirrors
 * base: centos-mirror.rbc.ru
 * extras: centos-mirror.rbc.ru
 * updates: centosc6.centos.org
nginx-1.14.0-1.el7_4.ngx.src.rpm

# Устанавливаем
$ rpm -i nginx-1.14.0-1.el7_4.ngx.src.rpm

# создаём структуру каталогов для rpm-пакета
$ rpmdev-setuptree

# устанавливаем зависимости для сборки пакета nginx
$ sudo yum-builddep rpmbuild/SPECS/nginx.spec

# убеждаемся, что Nginx Успешно собирается без наших правок
$ rpmbuild -ba rpmbuild/SPECS/nginx.spec
...
exit 0

# клонируем VTS-модуль
$ git clone https://github.com/vozlt/nginx-module-vts.git

# упаковываем в архив
$ tar -czf rpmbuild/SOURCES/nginx-module-vts.tar.gz nginx-module-vts/

# Правим spec-файл, чтобы привести примерно к следующему виду 
# строка 51 - добавили `_ft` в релиз, чтобы отличать оригинальный от нашего
# добавили строчку 81 - Source14 - архив с модулем
# добавили строчку 107 - распаковка архива в корень с исходниками
$ vim rpmbuild/SPECS/nginx.spec 
...
51 %define main_release 1%{?dist}.ngx_ft
...
78 Source11: nginx-debug.service
79 Source12: COPYRIGHT
80 Source13: nginx.check-reload.sh
81 Source14: nginx-module-vts.tar.gz
82 
83 License: 2-clause BSD-like license
...
99 %prep
100 %setup -q
101 cp %{SOURCE2} .
102 sed -e 's|%%DEFAULTSTART%%|2 3 4 5|g' -e 's|%%DEFAULTSTOP%%|0 1 6|g' \
103     -e 's|%%PROVIDES%%|nginx|g' < %{SOURCE2} > nginx.init
104 sed -e 's|%%DEFAULTSTART%%||g' -e 's|%%DEFAULTSTOP%%|0 1 2 3 4 5 6|g' \
105     -e 's|%%PROVIDES%%|nginx-debug|g' < %{SOURCE2} > nginx-debug.init
106 
107 %{__tar} -xvf %{SOURCE14}
108 
109 
110 %build
111 ./configure %{BASE_CONFIGURE_ARGS} \
...
```

Проверяем что всё ок вставили: `rpmbuild -bp rpmbuild/SPECS/nginx.spec`

Теперь, собственно, добавим сборку нашего модуля (статически) в nginx:
```bash
$ vim rpmbuild/SPECS/nginx.spec
58 %define BASE_CONFIGURE_ARGS $(echo "--prefix=%{_sysconfdir}/nginx ... --with-stream_ssl_preread_module --add-module=./nginx-module-vts")

# запускаем сборку
$ rpmbuild -ba rpmbuild/SPECS/nginx.spec
...
Wrote: /home/manager/rpmbuild/SRPMS/nginx-1.14.0-1.el7_4.ngx_ft.src.rpm
Wrote: /home/manager/rpmbuild/RPMS/x86_64/nginx-1.14.0-1.el7_4.ngx_ft.x86_64.rpm
Wrote: /home/manager/rpmbuild/RPMS/x86_64/nginx-debuginfo-1.14.0-1.el7_4.ngx_ft.x86_64.rpm
Executing(%clean): /bin/sh -e /var/tmp/rpm-tmp.I2PKL5
+ umask 022
+ cd /home/manager/rpmbuild/BUILD
+ cd nginx-1.14.0
+ /usr/bin/rm -rf /home/manager/rpmbuild/BUILDROOT/nginx-1.14.0-1.el7_4.ngx_ft.x86_64
+ exit 0
```

Возрадуемся!

```bash
# Устанавлиаем наш собранный пакет:
sudo yum localinstall rpmbuild/RPMS/x86_64/nginx-1.14.0-1.el7_4.ngx_ft.x86_64.rpm
sudo systemctl restart nginx

# Проверяем работоспособность
$ curl test-1
Yohoo, it works
# Иха!
```


#### Включение vts модуля

Итак, осталось отредактировать конфиг сервера, чтобы получить метрики.

[Документация](https://github.com/vozlt/nginx-module-vts#synopsis).  
Необходимо в конфиге `1-test.conf` включить вывод в формате `prometheus` и показать вывод.

[Подсказка для тех, у кого ну никак не получилось](https://gist.github.com/Frodox/23572a2098ba8ba96914e78fca5c52be) :)

#### Доп. Задания

* Как убедиться что в системе nginx собран с модулем VTS (посмотреть вкомпиленные модули?)
* Со звёздочкой и по желанию --- скомпилировать nginx с модулем [Lua](https://github.com/openresty/lua-nginx-module) или [Njs](https://github.com/nginx/njs). Поиграться с ними на основе примеров в документации.


Всё.
