from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_fingerprint', models.CharField(help_text='Browser/device identifier', max_length=255)),
                ('device_name', models.CharField(blank=True, help_text="e.g., 'Chrome on Windows'", max_length=200)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('access_token_jti', models.CharField(help_text='JWT ID for access token', max_length=255, unique=True)),
                ('refresh_token_jti', models.CharField(help_text='JWT ID for refresh token', max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(help_text='When the refresh token expires')),
                ('status', models.CharField(choices=[('active', 'Active'), ('revoked', 'Revoked'), ('expired', 'Expired')], default='active', max_length=20)),
                ('logout_reason', models.CharField(blank=True, help_text='Reason for logout/revocation', max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_sessions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['user', 'status'], name='user_session_user_id_status_idx'),
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['access_token_jti'], name='user_session_access_token_jti_idx'),
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['refresh_token_jti'], name='user_session_refresh_token_jti_idx'),
        ),
    ]
