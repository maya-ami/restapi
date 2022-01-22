# restapi

## Установка и запуск

0. Запустить postgresql на localhost.
1. Установить зависимости: `pip install -r requirements.txt`
2. Запустить `python create_db.py` для создания и заполнения игрушечной БД.
3. Проверить БД, запустив `python check_db.py`.
4. `python app.py` запустит приложение на 127.0.0.1:5000.

## Доступные эндпоинты

*Для всех пользователей:*

**GET**

  `/api/region` - возвращает выборку всех регионов.

  `/api/region/<region_id>` - возвращает информацию по одному региону. id региона передавать в url строке.

  `/api/city` - возвращает выборку всех городов.

  `/api/city/<city_id>` - возвращает информацию по одному городу. id города передавать в url строке.

  `/api/city/region_name/<region_name>` - возвращает выборку городов по названию региона. Название региона передавать в url строке.

  `/api/city/region_id/<region_id>` - возвращает выборку городов по id региона. id региона передавать в url строке.

**POST**

  `/api/login` - авторизация с помощью BasicAuth. Если пользователь зарегистрирован, возвращает токен, передаваемый в header для обращения к эндпоинтам, где требуется авторизация.

*Для авторизованных пользователей:*

**POST**

  `/api/region` - добавляет новый регион в базу данных. В запросе отправить json типа {"id": 9, "name": "Krasnodarskiy krai"}.
  `/api/city` - добавляет новый город в базу данных. В запросе отправить json типа {"id": 10, "name": "Uchaly", "region_id": 1}.

**PUT**

  `/api/region` - изменяет информацию о регионе в базе данных. В запросе отправить json типа {"id": 1, "name": "Bashkiria"}.
  `/api/city` - изменяет информацию о городе в базе данных. В запросе отправить json типа {"id": 1, "name": "City of Ufa", "region_id": 1}.

**DELETE**

  `/api/region/<region_id>` - удаляет информацию о регионе в базе данных. id региона передавать в url строке.
  `/api/city/<city_id>` - удаляет информацию о городе в базе данных. id города передавать в url строке.
