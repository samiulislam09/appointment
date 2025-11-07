from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile, CustomerProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample users and profiles for testing'

    def handle(self, *args, **kwargs):
        # Create sample providers
        providers_data = [
            {
                'username': 'dr_smith',
                'email': 'smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'specialization': 'Business Consulting',
                'bio': 'Expert in business strategy and management consulting with 10+ years experience.',
                'phone': '123-456-7890'
            },
            {
                'username': 'dr_johnson',
                'email': 'johnson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'specialization': 'Financial Advisory',
                'bio': 'Certified financial advisor specializing in corporate finance.',
                'phone': '123-456-7891'
            },
            {
                'username': 'dr_williams',
                'email': 'williams@example.com',
                'first_name': 'Michael',
                'last_name': 'Williams',
                'specialization': 'Legal Consulting',
                'bio': 'Corporate lawyer with expertise in business law and contracts.',
                'phone': '123-456-7892'
            },
        ]

        for provider_data in providers_data:
            user, created = User.objects.get_or_create(
                username=provider_data['username'],
                defaults={
                    'email': provider_data['email'],
                    'first_name': provider_data['first_name'],
                    'last_name': provider_data['last_name'],
                    'role': User.PROVIDER,
                    'phone': provider_data['phone']
                }
            )
            
            if created:
                user.set_password('password123')  # Default password
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created provider user: {user.username}'))
            
            # Create or update provider profile
            profile, profile_created = ProviderProfile.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': provider_data['specialization'],
                    'bio': provider_data['bio'],
                    'is_approved': True
                }
            )
            
            if profile_created:
                self.stdout.write(self.style.SUCCESS(f'Created provider profile for: {user.username}'))

        # Create sample customers
        customers_data = [
            {
                'username': 'alice_customer',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Brown',
                'company': 'Tech Corp',
                'phone': '123-456-7893'
            },
            {
                'username': 'bob_customer',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Davis',
                'company': 'Innovation Inc',
                'phone': '123-456-7894'
            },
        ]

        for customer_data in customers_data:
            user, created = User.objects.get_or_create(
                username=customer_data['username'],
                defaults={
                    'email': customer_data['email'],
                    'first_name': customer_data['first_name'],
                    'last_name': customer_data['last_name'],
                    'role': User.CUSTOMER,
                    'phone': customer_data['phone']
                }
            )
            
            if created:
                user.set_password('password123')  # Default password
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created customer user: {user.username}'))
            
            # Create or update customer profile
            profile, profile_created = CustomerProfile.objects.get_or_create(
                user=user,
                defaults={'company': customer_data['company']}
            )
            
            if profile_created:
                self.stdout.write(self.style.SUCCESS(f'Created customer profile for: {user.username}'))

        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Created Successfully ==='))
        self.stdout.write(self.style.SUCCESS('Provider accounts (username/password):'))
        self.stdout.write('  - dr_smith / password123')
        self.stdout.write('  - dr_johnson / password123')
        self.stdout.write('  - dr_williams / password123')
        self.stdout.write(self.style.SUCCESS('\nCustomer accounts (username/password):'))
        self.stdout.write('  - alice_customer / password123')
        self.stdout.write('  - bob_customer / password123')