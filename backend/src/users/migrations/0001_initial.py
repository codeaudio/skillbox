# Generated by Django 4.2 on 2023-04-14 02:19

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[users.validators.username_validator], verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='адрес почты')),
                ('first_name', models.CharField(blank=True, max_length=35, null=True, verbose_name='Имя пользователя')),
                ('last_name', models.CharField(blank=True, max_length=35, null=True, verbose_name='Фамилия пользователя')),
                ('password', models.CharField(max_length=90, validators=[users.validators.password_validator], verbose_name='Пароль пользователя')),
                ('is_confirm', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'db_table': 'user',
                'ordering': ['-id'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ConfirmCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='confirms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Код подтверждения пользователя',
                'verbose_name_plural': 'Коды подтверждения пользователя',
                'db_table': 'confirm_code',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='AuthCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('exp', models.DateTimeField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Авторизационный код',
                'verbose_name_plural': 'Авторизационные коды',
                'db_table': 'auth_code',
                'ordering': ['-id'],
            },
        ),
    ]
