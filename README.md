# Описание.

_Дипломный проект на учебном сервере от Яндекс._

## Технологии:
* Python 3.7
* Django 3.2
* PostgreSQL
* DRF
* Docker
* Nginx

Проект представляет из себя социальную сеть для обмена фотографиями любимых рецептов.
Проект состоит из бэкенд-приложения на Django и фронтенд-приложения на React.


При запуске проекта через Джанго-админку необходимо вручную добавить Тэги для рецептов.
Пример создания Тэгов:
![image](https://github.com/RiSSoL-86/foodgram-project-react/assets/110422516/c976d647-0bb8-49cc-a867-0fb5ce9379ee)

![image](https://github.com/RiSSoL-86/foodgram-project-react/assets/110422516/76c64cd7-3700-4626-aa4f-8a075492079f)


Для дальнейшей работы, необходимо добавить список ингридиентов, которые будут использоваться в рецептах.
Список ингридиентов, уже подготовлен, он находится в папке - data/ingredients.csv
Добавление списка ингридиентов выполняется через Джанго-админку, кнопкой 'ИМПОРТ' во вкладке ингридиенты.
Процесс добавления ингридиентов:
![image](https://github.com/RiSSoL-86/foodgram-project-react/assets/110422516/ddea3b57-457d-459d-879e-f0ddce751d9e)

![image](https://github.com/RiSSoL-86/foodgram-project-react/assets/110422516/6a77b9a9-d5da-4fd0-a020-6e91a6af74ab)


Пример работы сайта:
![image](https://github.com/RiSSoL-86/foodgram-project-react/assets/110422516/787dd0f7-a6dc-4a65-9eb6-b6b4cd4dd94b)

Сайт имеет свой API-сервис, при работе с которым можно регистрировать пользователей, получать/создавать рецепты и многое другое.
Чтобы ознакомиться с полным списком возможных API запросов, необходимо в папке infra, выполните команду: docker-compose up.
После чего по адресу http://localhost/api/docs/ — будет доступна API спецификация. 


Проект доступен по ссылке: https://rissol-foodgram.ddns.net/

Автор: Григорук Илья - https://github.com/RiSSoL-86
