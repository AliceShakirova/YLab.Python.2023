# YLab.Python.2023

Для запуска необходимо выполнить следующие действия:
1. git clone https://github.com/AliceShakirova/YLab.Python.2023.git
2. cd YLab.Python.2023
3. Создать .env-файлы в корневом каталоге репозитория (структуру файлов можно посмотреть в файлах **app.env.SAMPLE** и **pg.env.SAMPLE**)
3.1 файлы для контейнера с сервисом: **prod.app.env** и **prod.pg.env**
3.2 файлы для контейнера с сервисом и тестами: **test.app.env** и **test.pg.env**
4. Команда для запуска контейнера с сервисом:
    docker compose -f compose.yaml up --build
5. Команда для запуска контейнера с тестами:
    docker compose -f compose-tests.yaml up --build
Дополнительные задания со * и **:
ДЗ 2
1.Вывод меню и подменю одним запросом src/Repository/menu_repo.py функция "get_submenus_and_dishes_counts"
2.Тестовый сценарий Tests/test_scenario.py
ДЗ 3
1.Описать ручки API в соответствии с OpenAPI openapi.yaml
2.Аналог reverse() из Django conftest.py функция "func_reverse"
