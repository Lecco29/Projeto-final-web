# Instruções Rápidas de Execução

## ⚠️ Nota: Este projeto já está criado

Se você quiser criar um projeto similar do zero:

**Django:**
```bash
pip install django
django-admin startproject backend
cd backend
python manage.py startapp planner
```

**React (Vite):**
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

---

## Executar o Projeto Existente

### Backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Criar usuário (será usado como ID=1)
python manage.py runserver
```

## Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## Acessar

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

## Primeiros Passos

1. Certifique-se de que o backend está rodando
2. Crie um superusuário com `python manage.py createsuperuser`
3. Acesse o frontend e comece a cadastrar ativos
4. Registre histórico de dividendos
5. Crie uma meta de renda
6. Execute uma simulação

