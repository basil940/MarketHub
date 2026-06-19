import argparse
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomsite.settings')

import django
django.setup()

from users.models import User

parser = argparse.ArgumentParser(description='Create or update a test user.')
parser.add_argument('--username', default='testuser', help='Username for the test user')
parser.add_argument('--password', default='testpass123', help='Password for the test user')
parser.add_argument('--email', default='test@example.com', help='Email address for the test user')
parser.add_argument('--phone', default='+91-9876543210', help='Phone number for the test user')
args = parser.parse_args()

user, created = User.objects.get_or_create(
    username=args.username,
    defaults={'email': args.email, 'phone': args.phone}
)

user.email = args.email
user.phone = args.phone
user.set_password(args.password)
user.save()

if created:
    print('✅ Test user created successfully!')
else:
    print('✅ Test user updated successfully!')

print(f'Username: {args.username}')
print(f'Password: {args.password}')
print(f'Email: {args.email}')
