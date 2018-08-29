### Описание

На этом занятии мы поговорим о configuration management на примере Ansible.

### Домашнее задание

В рамках домашнего задания вы напишете роль для postgresql и nginx, который будет взаимодействовать с django приложением.

На протяжении всех заданий будем считать, что ваш сервер находится в группе [webservers]

#### Задание 1. Nginx role

* Склонируйте к себе репозиторий с ролью nginx, рассмотренный на лекции: https://gitlab.com/tfs_s18_admin/homework
* В данной роли замените статичный сайт, соответствующий {{ inventory_hostname }} на проксирование запросов до django приложения.
* У вас должен быть определен блок upstream вида:
```
upstream django {
    server s-##.fintech-admin.m1.tinkoff.cloud:8000;
}
```
а также блок server:
```
server {

    listen 80;
    server_name s-##.fintech-admin.m1.tinkoff.cloud;

    client_max_body_size 50m;

    location / {
        proxy_http_version          1.1;
        proxy_set_header Accept-Encoding "";
        proxy_pass                  http://django;
        proxy_set_header            Host $host;
        proxy_set_header            X-Forwarded-For $remote_addr;
        proxy_set_header            X-Real-IP $remote_addr;
        proxy_set_header            X-Forwarded-Proto $scheme;
        proxy_connect_timeout       500ms;
    }
}
```

* Создайте новый репозиторий в своем проекте на http://bitbucket.fintech-admin.m1.tinkoff.cloud
* Закоммитьте туда обновленный репозиторий с nginx role.

Мы считаем, что у вас задеплоено приложение на django, которое слушает на порте 8000.

Таким образом, при обращении http://s-##.fintech-admin.m1.tinkoff.cloud мы увидим форму, отдаваемую приложением django.

#### Задание 2. PostgreSQL role

В рамках данного задания вы напишете роль для развертывания сервера postgresql, а также дополнительную роль, 
которая создаст на нем начальные структуры.

* Создадим роль, устанавливающая postgres.
* Создайте defaults/main.yml:

```
postgres_work_mem: 32MB
postgres_shared_buffers: 512MB

postgres_listen_port: 6789
postgres_listen_interface: "*"

postgres_data_dir: /var/lib/pgsql/data
```

* Используйте модуль yum для установки пакета postgresql-server
* Используйте модуль stat для получения информации о файле:

```
  - name: get db exist status
    stat:
      path: "{{ postgres_data_dir }}/PG_VERSION"
    register: pgdata
```

* Создавайте базу если она отсутствует

```
  - name: Ensure PostgreSQL database is initialized.
    command: "sudo -u postgres bash -c 'initdb -D {{ postgres_data_dir }}'"
    when: not pgdata.stat.exists
```

* Создайте конфиг сервера postgresql.conf и pg_hba.conf конфигурацию доступов используя модуль template
Убедитесь, что у вас есть local доступ для пользователя postgres.

```
local   all            postgres                         trust
```

* Используя yum установите пакет python-pip.
* Используя модуль pip установите пакет psycopg2.
* Используя модуль service убедите, что сервер запущен и в статусе enabled.

* Создайте роль, которая заполняет тестовыми данными postgresql-fill
* Создайте defaults/main.yml:

```
postgres_postgres_password:

postgres_test_db: test
postgres_test_username: test-user
postgres_test_user_password:
```

Поменяйте данные так как это нужно в вашем приложении

Обратите внимание, что мы не заполняем поля, соответствующие паролям.
* Создайте в корне репозитория файл .vault_pass.txt и запишите в него пароль для шифрования секретов.
* Укажите в ansible.cfg путь к данному файлу:

```
vault_password_file = .vault_pass.txt
```

Не забудьте добавить этот файл в .gitignore:

```
/.vault_pass.txt
```

Когда мы будем проверять, мы будем предполагать, что шифрующий ключ - password.
Если он отличается, напишите его вместе с ссылкой на ваш репозиторий.
* Предположим, что группа, содержащая ваш Создайте файл playbooks/group_vars/webservers/vars.yml

```
postgres_postgres_password: "{{ vault_postgres_postgres_password }}"
postgres_test_user_password: "{{ vault_postgres_test_user_password }}"
```

* Создадим зашифрованный файл:

```
ansible-vault create playbooks/group_vars/webservers/vault.yml
```

* И заполним его в открывшемся редакторе (по-умолчанию vim)

```
vault_postgres_postgres_password: password
vault_postgres_test_user_password: password
```

* Давайте напишем таски, создающие нужные сущности. Мы специально оставили local postgres trust в pg_hba.conf, 
чтобы не нужно было атворизовываться при запуске данных модулей.
* Используйте модуль postgresql_user чтобы установить пароль пользователю postgres.

```
- name: Create management user
  postgresql_user:
    name: postgres
    password: "{{ postgres_postgres_password }}"
```

* Используйте модуль postgresql_db, чтобы создать базу.
* Используйте модуль postgresql_user, чтобы создать тестового пользователя.
* Используйте модуль postgresql_privs, чтобы выдать привилегии тестовому пользователю к тестовой базе.

```
- name: Add grants
  postgresql_privs:
    database: "{{ postgres_test_db }}"
    grant_option: yes
    privs: ALL
    type: database
    role: "{{ postgres_test_username }}"
```

Созданную роль необходимо будет добавить в созданный репозиторий на http://bitbucket.fintech-admin.m1.tinkoff.cloud

Проверяя вашу роль, мы добавим файл .vault_pass.txt и попробуем раскатить ваши роли на тестовом хосте и проверить, что они работают.

Убедитесь, что вся конфигурация содержится в ролях, и вы не выполняли никаких ручных действий для обеспечения работы.