## Quickstart

### 1. Clone repository


### 2. Install dependecies and Python >=3.10


### create a virtualenv

```
$ python -m venv venv
```
ou
```
$ python3 -m venv venv
```

### Active a virtualenv

```
$ venv/scripts/activate
```

linux
```
$ source venv/bin/activate
```

### Run with Python >=3.10 and pip:
```
$ pip install -r requirements.txt
```
ou
```
$ pip3 install -r requirements.txt

```
### Crie um arquivo .env na raiz do projeto

```
SECURITY__JWT_SECRET_KEY=DVnFmhwvjEhJZpuhndxjhlezxQPJmBIIkMDEmFREWQADPcUnrG
SECURITY__BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]
SECURITY__ALLOWED_HOSTS=["localhost", "127.0.0.1"]

DATABASE__HOSTNAME=localhost
DATABASE__USERNAME=rDGJeEDqAz
DATABASE__PASSWORD=XsPQhCoEfOQZueDjsILetLDUvbvSxAMnrVtgVZpmdcSssUgbvs
DATABASE__PORT=5455
DATABASE__DB=default_db
```

### 3. Setup database and migrations

```bash
### Setup database
docker-compose up -d

### Run Alembic migrations
alembic upgrade head
```

### 4. Now you can run app

```bash
### And this is it:
uvicorn app.main:app --reload

```
