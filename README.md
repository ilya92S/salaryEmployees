
#### Алгоритм агрегации статистических данных о зарплатах сотрудников компании по временным промежуткам.

---
#### Коротко о данных в БД
Для импорта коллекции, нужна установленная `mongod.exe` и `mongorestore.exe`, с настроенной средой в `path`. Запустив сервер в новом окне прописываем команду:
```bash
mongorestore --db sampleDB --collection sample_collection C:\sampleDB\sample_collection.bson
```

у нас будет готовая коллекция.

##### Для запуска:

1. Установить все пакеты из `requirements.txt`
2. Получить токен у BotFather для работы библиотеки `aiogram`
3. Для получения данных из `MongoDB`, нужно запустить сервер
4. Для нормального функционирования программы должна быть соответствующая БД с коллекцией
