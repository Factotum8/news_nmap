# News nmap
It is test [task](https://docs.google.com/document/d/1PZREzOfBAgqwHDdaWUaPLKtJV0dkTsaqoI_fgmj3Z_o/edit) by applying for job.

## Run
```
news_nmap.py:
```
1.	В терминале или в командной строке window, перейти в директорию проекта `news_nmap` (она содержит этот README.md файл). 
2. Выполнить комманду: `pip3 install --no-cache-dir -e .[test]`
3.	Создайте файл `.env` (шаблон файла .env.yaml.default) или настройте переменные окружения (названия переменных указаны в .env.yaml.default).
4.	Выполните следующую команду: `python ./news_nmap/news_nmap.py -p ./.env`.

```
docker-compose
```
1. В терминале или в командной строке window, перейти в директорию проекта `news_nmap` (она содержит этот README.md файл).
2. Выполнить комманду: `docker-compose build`
3. Выполнить комманду: `docker-compose up`
```
run unit tests
```
1.	В терминале или в командной строке window, перейти в директорию проекта `news_nmap`.
2. Выполнить комманду: `pip3 install --no-cache-dir -e .[test]`
3.	Выполните следующую команду: `python -m unittest discover ./tests/unittests/`.

```
Code coverage
```
1. В терминале или в командной строке window, перейти в директорию проекта `news_nmap/`.
2. Выполнить комманду: `pip3 install --no-cache-dir -e .[test]`
3. Выполните следующую команду: `coverage run --source=./mypackages,./news_nmap -m unittest discover ./tests/unittests/`
4. Выполните следующую команду: `coverage html`  
**Output** Каталог htmlcov отчёт о тестовом покрытие доступен по пути `./htmlcov/index.html` 

## License
[MIT](LICENSE)
