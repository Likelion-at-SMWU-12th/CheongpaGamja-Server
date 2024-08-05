# users/migrations/0002_add_initial_interests.py
from django.db import migrations

def create_initial_interests(apps, schema_editor):
    Interest = apps.get_model('users', 'Interest')
    interests = [
    ('가치관', '가치관'),
    ('재테크', '재테크'),
    ('사랑', '사랑'),
    ('생활지식', '생활지식'),
    ('인간관계', '인간관계'),
    ('진로', '진로'),
    ]
    for name, display_name in interests:
        Interest.objects.get_or_create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_interests),
    ]
