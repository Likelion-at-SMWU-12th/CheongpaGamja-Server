from datetime import datetime, timedelta
from django.utils.timesince import timesince
from django.utils.timezone import now

# 채팅방 날짜를 유저가 파악하기 쉽게 바꿔줌.
def time_difference(date):
    current_time = now()
    difference = current_time - date

    if difference < timedelta(minutes=1):
        return "방금 전"
    elif difference < timedelta(hours=1):
        return f"{int(difference.total_seconds() // 60)}분 전"
    elif difference < timedelta(days=0.5):
        return f"{int(difference.total_seconds() // 3600)}시간 전"
    elif difference < timedelta(days=1):
        return "오늘"
    elif difference < timedelta(days=2):
        return "어제"
    elif difference < timedelta(days=30):
        return f"{difference.days}일 전"
    elif difference < timedelta(days=60):
        return "1달 전"
    elif difference < timedelta(days=365):
        months = difference.days // 30
        return f"{months}달 전"
    else:
        years = difference.days // 365
        return f"{years}년 전"