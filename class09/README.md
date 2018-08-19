#### **1. Простой html-сайт**
Чтобы запросы с рабочей машины по имени `test-1` и `test-2` приходили на неё же, добавляем в файл `/etc/hosts` следующие записи.
В данном случае это будет как запрос, который обычно разрешает доменное имя DNS'ом. Устанавливаем IP адрес рабочей машины, на который
хотим чтобы наш локальный компьютер пошел, обрабатывая запрос доменного имени.
```bash
10.219.180.23 test-1
10.219.180.23 test-2
```
Nginx слушает на 8080 порту, поэтому всё запросы проверяются следующим образом:
```bash
curl test-1:8080
curl test-2:8080
```
Иначе ответ идет от **former**, который запущен на 80 порту.
Серверу направляется запрос, nginx проверяет поле “Host” заголовка запроса. Конфигурационным файлом по умолчанию считается `/etc/nginx/nginx.conf` в нем могут быть прописаны все настройки, но в нашем случае содержится следующая строка:
```bash
include /etc/nginx/conf.d/*.conf;
```
Таким образом, все конфигурационные файлы серверов будут просматриваться в этой директории.
Так как конфигурационный файл `1-test.conf` был первым в списке, то сервер `test-1` считался сервером по умолчанию для этого порта. После того как сервером по умолчанию был сделан `s-14`, то если значение не соответствует ни одному из имён серверов или в заголовке запроса нет этого поля вовсе, nginx направлеяет запрос в этот сервер.

### **2. Сборка и запуск Nginx с VTS-модулем**
Для того, чтобы можно было увидеть vts как на каритнках поменяла default_server поменяла на test-1, так как имя test-1 не разрешается dns'ом и невозможно посмотреть.

http://s-14.fintech-admin.m1.tinkoff.cloud:8080/status - в формате prometheus

http://s-14.fintech-admin.m1.tinkoff.cloud:8080/status_vhost - в формате html

Команда `nginx -V` выводит список всех модулей, которые включены в состав пакета.
```bash
[user14@s-14 ~]$ nginx -V
nginx version: nginx/1.14.0
built by gcc 4.8.5 20150623 (Red Hat 4.8.5-28) (GCC)
built with OpenSSL 1.0.2k-fips  26 Jan 2017
TLS SNI support enabled
configure arguments: --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --modules-path=/usr/lib64/nginx/modules 
--conf path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log 
--pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp 
--http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp 
--http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx 
--group=nginx --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module 
--with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module 
--with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module 
--with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module 
--with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module 
--with-stream_ssl_preread_module --with-stream_ssl_preread_module 
--add-module=./nginx-module-vts 
--add-module=./ngx_devel_kit-0.3.1rc1 
--add-module=./lua-nginx-module-0.10.13 
--add-module=./njs/nginx 
--with-cc-opt='-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong 
--param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -fPIC' --with-ld-opt='-Wl,-z,relro -Wl,-z,now -pie'
```
