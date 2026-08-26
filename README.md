<p align="center">
  <img src="./resources/extras/logo_readme.jpg" alt="TeamTeleFriend Logo">
</p>
<h1 align="center">
  <b>TeleFriend - UserBot</b>
</h1>

<b>Стабильный плагинный Telegram userbot + музыкальный бот для голосовых и видеозвонков, основанный на Telethon.</b>

[![](https://img.shields.io/badge/TeleFriend-v0.8-crimson)](#)
[![Stars](https://img.shields.io/github/stars/TeamTeleFriend/TeleFriend?style=flat-square&color=yellow)](https://github.com/TeamTeleFriend/TeleFriend/stargazers)
[![Forks](https://img.shields.io/github/forks/TeamTeleFriend/TeleFriend?style=flat-square&color=orange)](https://github.com/TeamTeleFriend/TeleFriend/fork)
[![Size](https://img.shields.io/github/repo-size/TeamTeleFriend/TeleFriend?style=flat-square&color=green)](https://github.com/TeamTeleFriend/TeleFriend/)   
[![Python](https://img.shields.io/badge/Python-v3.10+-blue)](https://www.python.org/)
[![CodeFactor](https://www.codefactor.io/repository/github/teamultroid/ultroid/badge/main)](https://www.codefactor.io/repository/github/teamultroid/ultroid/overview/main)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TeamTeleFriend/TeleFriend/graphs/commit-activity)
[![Docker Pulls](https://img.shields.io/docker/pulls/theteamultroid/ultroid?style=flat-square)](https://img.shields.io/docker/pulls/theteamultroid/ultroid?style=flat-square)   
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/TeamTeleFriend/TeleFriend)
[![Contributors](https://img.shields.io/github/contributors/TeamTeleFriend/TeleFriend?style=flat-square&color=green)](https://github.com/TeamTeleFriend/TeleFriend/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![License](https://img.shields.io/badge/License-AGPL-blue)](https://github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE)
----

# Развёртывание
- [Heroku](#deploy-to-heroku)
- [Okteto](#deploy-to-okteto)
- [Локальная машина](#deploy-locally)

# Документация 
[![Documentation](https://img.shields.io/badge/Documentation-TeleFriend-blue)](http://ultroid.tech/)

# Учебник 
- Полное руководство - [![Полное руководство](https://img.shields.io/badge/Watch%20Now-blue)](https://www.youtube.com/watch?v=0wAV7pUzhDQ)

- Руководство по получению URL и пароля Redis - [здесь.](./resources/extras/redistut.md)
---

## Развёртывание на Heroku
Получите [Необходимые переменные](#Necessary-Variables) и затем нажмите кнопку ниже!  

<summary>Развёртывание на Heroku</summary>
<p>
<br>
<a href="https://heroku.com/deploy">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
</a>
</p>
## Развёртывание на Okteto
Получите [Необходимые переменные](#Necessary-Variables) и затем нажмите кнопку ниже!

[![Develop on Okteto](https://okteto.com/develop-okteto.svg)](https://cloud.okteto.com/deploy?repository=https://github.com/TeamTeleFriend/TeleFriend)

## Локальное развёртывание
- [Традиционный метод](#local-deploy---traditional-method)
- [Простой метод](#local-deploy---easy-method)
- [TeleFriend CLI](#ultroid-cli)

### Локальное развёртывание - Простой метод
- Linux - `wget -O locals.py https://git.io/JY9UM && python3 locals.py`
- Windows - `cd desktop ; wget https://git.io/JY9UM -o locals.py ; python locals.py`
- Termux - `wget -O install-termux https://tiny.ultroid.tech/termux && bash install-termux`

### Локальное развёртывание - Традиционный метод
- Получите ваши [Необходимые переменные](#Necessary-Variables)
- Клонируйте репозиторий:    
`git clone https://github.com/TeamTeleFriend/TeleFriend.git`
- Перейдите в клонированную папку:    
`cd TeleFriend`
- Создайте виртуальное окружение:      
`virtualenv -p /usr/bin/python3 venv`
`. ./venv/bin/activate`
- Установите зависимости:      
`pip(3) install -U -r re*/st*/optional-requirements.txt`
`pip(3) install -U -r requirements.txt`
- Сгенерируйте вашу `SESSION`:
  - Для пользователей Linux:
    `bash sessiongen`
     или
    `wget -O session.py https://git.io/JY9JI && python3 session.py`
  - Для пользователей Termux:
    `wget -O session.py https://git.io/JY9JI && python session.py`
  - Для пользователей Windows:
    `cd desktop ; wget https://git.io/JY9JI -o ultroid.py ; python ultroid.py`
- Заполните ваши данные в файле `.env`, как указано в [`.env.sample`](https://github.com/TeamTeleFriend/TeleFriend/blob/main/.env.sample).
(Вы можете либо отредактировать и переименовать файл, либо создать новый файл с именем `.env`.)
- Запустите бота:
  - Пользователи Linux:
   `bash startup`
  - Пользователи Windows:
    `python(3) -m pyTeleFriend`

---
## Необходимые переменные
- `SESSION` - Строка сессии для сессии входа в ваш аккаунт. Получите её [здесь](#Session-String)

Одна из следующих баз данных:
- Для **Redis** (руководство [здесь](./resources/extras/redistut.md))
  - `REDIS_URI` - URL конечной точки Redis, с [redislabs](http://redislabs.com/).
  - `REDIS_PASSWORD` - Пароль конечной точки Redis, с [redislabs](http://redislabs.com/).
- Для **MONGODB**
  - `MONGO_URI` - Получите его с [mongodb](https://mongodb.com/atlas).
- Для **SQLDB**
  - `DATABASE_URL`- Получите его с [elephantsql](https://elephantsql.com).

## Строка сессии
Различные способы получить вашу `SESSION`:
* [![Run on Repl.it](https://replit.com/badge/github/TeamTeleFriend/TeleFriend)](https://replit.com/@TeamTeleFriend/TeleFriendStringSession)
* Linux : `wget -O session.py https://git.io/JY9JI && python3 session.py`
* PowerShell : `cd desktop ; wget https://git.io/JY9JI ; python ultroid.py`
* Termux : `wget -O session.py https://git.io/JY9JI && python session.py`
* TelegramBot : [@SessionGeneratorBot](https://t.me/SessionGeneratorBot)

---

# Основная команда контрибьюторов

<table>
  <tr>
    <td align="center"><a href="https://github.com/xditya"><img src="https://avatars.githubusercontent.com/xditya" width="75px;" alt=""/><br/><sub><b>@xditya</b></sub></a></td>
    <td align="center"><a href="https://github.com/1danish-00"><img src="https://avatars.githubusercontent.com/1danish-00" width="75px;" alt=""/><br/><sub><b>@1danish_00</b></sub></a></td>
    <td align="center"><a href="https://github.com/buddhhu"><img src="https://avatars.githubusercontent.com/buddhhu" width="75px;" alt=""/><br/><sub><b>@buddhhu</b></sub></a></td>
    <td align="center"><a href="https://github.com/TechiError"><img src="https://avatars.githubusercontent.com/TechiError" width="75px;" alt=""/><br/><sub><b>@TechiError</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/New-dev0"><img src="https://avatars.githubusercontent.com/New-dev0" width="75px;" alt=""/><br/><sub><b>@New-dev0</b></sub></a></td>
    <td align="center"><a href="https://github.com/ArnabXD"><img src="https://avatars.githubusercontent.com/ArnabXD" width="75px;" alt=""/><br/><sub><b>@Arnab431</b></sub></a></td>
    <td align="center"><a href="https://github.com/sppidy"><img src="https://avatars.githubusercontent.com/sppidy" width="75px;" alt=""/><br/><sub><b>@sppidy</b></sub></a></td>
    <td align="center"><a href="https://github.com/Atul-Kumar-Jena"><img src="https://avatars.githubusercontent.com/Atul-kumar-Jena" width="75px;" alt=""/><br/><sub><b>@hellboi_atul</b></sub></a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/iAkashPattnaik"><img src="https://avatars.githubusercontent.com/iAkashPattnaik" width="75px;" alt=""/><br/><sub><b>@iAkashPattnaik</b></sub></a></td>
  </tr>
</table>

## Контрибьюторы

<a href="https://github.com/TeamTeleFriend/TeleFriend/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=TeamTeleFriend/TeleFriend" />
</a>

Мы очень благодарны за все вклады, сделанные нашей удивительной сообществом! ❤️

---

# Лицензия
[![License](https://www.gnu.org/graphics/agplv3-155x51.png)](LICENSE)   
TeleFriend распространяется под [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) версии 3 или выше.


---
# Благодарности
* [![TeamTeleFriend-Devs](https://img.shields.io/static/v1?label=Teamultroid&message=devs&color=critical)](https://t.me/TeleFriendDevs)
* [Lonami](https://github.com/LonamiWebs/) за [Telethon.](https://github.com/LonamiWebs/Telethon)
* [MarshalX](https://github.com/MarshalX) за [PyTgCalls.](https://github.com/MarshalX/tgcalls)

> Сделано с 💕 от [@TeamTeleFriend](https://t.me/TeamTeleFriend).    
