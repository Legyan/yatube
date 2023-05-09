# Yatube

Социальная сеть

[![CI](https://github.com/legyan/yatube/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/legyan/hw05_final/actions/workflows/python-app.yml)

[```legyan.pythonanywhere.com```](http://legyan.pythonanywhere.com/)


### Описание

Yatube — социальная сеть, которая позволяет пользователям создавать публикации на различные темы, комментировать их, а также подписываться на других авторов. 

### Стек технологий 

![](https://img.shields.io/badge/Python-3.7-black?style=flat&logo=python) 
![](https://img.shields.io/badge/Django-2.2.1.6-black?style=flat&logo=django&logoColor=green)
![](https://img.shields.io/badge/Bootstrap-3-black?style=flat&logo=bootstrap)
![](https://img.shields.io/badge/SQLite-3.7.15-black?style=flat&logo=sqlite)

### Запуск проекта

1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Legyan/yatube.git
```

```
cd yatube
```

2. Cоздать и активировать виртуальное окружение:

```
python3.7 -m venv venv
```

* Для Linux/macOS

    ```
    source venv/bin/activate
    ```

* Для Windows

    ```
    source venv/scripts/activate
    ```

3. Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

4. Выполнить миграции:

```
python yatube/manage.py migrate
```

5. Запустить сервер:

```
python yatube/manage.py runserver
```
