# 청파동감자 백엔드 레포

## 프론트에서 서버 pull 받고 실행하는 법
1. 가상환경 설치

    ```python -m venv 가상환경명```
2. 가상환경 실행

    ```source 가상환경명/scripts/activate```
    ```source 가상환경명/bin/activate```
3. requirements.txt에 있는 내용 다운받기

    ```pip install -r requirements.txt```
4. secrets.json을 메인 폴더에 넣어주기
5. DB 만들기
   
    ```python manage.py makemigrations```
    ```python manage.py migrate```

6. 서버 실행

    ```python manage.py runserver```
