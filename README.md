# AsynchronousBalancer
Asynchronous balancer on Python made as a part of test task for [ERASED] company internship.

# Swagger
localhost:8000/docs

# Запуск
Запустить Balancer и 5 Worker'ов. (Балансер на порту 8000, Воркеры на 8001, 8002...)

`docker-compose up`

# Запуск тестов 
Установим зависимости для тестов:

`pip install -r ./test/requirements.txt`

Из папки ./test запустим run.py:

`python3.10 run.py`

# Описание тестов

1) На протяжении 250 секунд на балансер будут посылаться запросы (Автоматически) 
2) На 100-ой секунде отключается worker1 через `docker-compose kill -s SIGKILL worker1` (Автоматически)
3) На 200-ой секунде worker1 рестартится через `docker-compose restart worker1` (Автоматически)
4) В конце вернется массив респонсов. Часть из них будет 'запятисочена' 

# Трактовка


Достаточными условиями для успешного тестирования при заданных настройках
(время выполнения задачи 15сек, 5 воркеров, 1 секунда задержки) будут:

1. Ни в один из моментов времени количество подключений у каждого сервера не может быть больше 4
2. Нагрузка распределяется линейно, относительно общего числа подключений в момент времени

2.1. При отключении воркера, нагрузка перераспределяется между оставшимися:

![Пруф 3](./test/proof3.png)

2.2. При повторном подключении воркера, нагрузка распределяется между ним и всеми живыми воркерами:

![Пруф 4](./test/proof4.png)

---
P.S.
Аргументацию пункта (1) см. в AsynchronousBalancer/test/proof1.png:

![Пруф 1](./test/proof1.png)

Учитываем, что есть запросы посылаются и обрабатываются не точно каждую 1 секунду, в связи с чем картинка 
proof1.png является идеальным примером Least Connections при заданных настройках.

Также на AsynchronousBalancer/test/proof2.png заметим, что после отключения крайних двух сессий воркер стал
самым незагруженным, в связи с чем следующие два подключения отдали ему:

![Пруф 2](./test/proof2.png)

Недостатком моего решения является то, что с появлением неактивного воркера время распределения задачи увеличивается
с AVERAGE_RESPONSE_TIME до HEALTHCHECK_TIMEOUT. Решается это добавлением ручки /register в балансер
(что лишает смысла писать для него конфиг), либо Scheduled проверкой воркеров на живучесть и хранением status
как свойства balancer.Worker, что тоже имеет свои недостатки(например, некоторые запросы могут пятисотить
просто потому, что мы распределили их в неработающий воркер до проверки на хелсчек).

-----------------------------------------------------------------------------------------------------------
В любом случае таймаут = 1 секунде, очевидно, не самое адекватное решение, т.к. запросы к локалхосту,
но в целях демонстрации подойдет.

# Зависимости
В воркере и балансере есть повторяющиеся зависимости(типа TaskStatus). Конечно, хорошо бы унифицировать, создав
библиотечку. Была также мысль организовать хранение тасок в бдшке какой-нибудь, но это вроде не требуется.
