"""Views tests."""
from http.cookies import SimpleCookie
from django.urls import reverse
from samples_manager.models import *
from django.test import TestCase, Client

def set_user_cookies(client, user_role):
    """Sets cookies for user."""
    cookies = SimpleCookie()

    if user_role == 'Admin':
        cookies['username'] = 'test-admin'
        cookies['first_name'] = 'Test'
        cookies['last_name'] = 'Admin'
        cookies['telephone'] = '1234'
        cookies['email'] = 'test-admin@gmail.com'
        cookies['mobile'] = '1234'
        cookies['department'] = 'EP/DT'
        cookies['home_institute'] = 'TU'
    elif user_role == 'User':
        cookies['username'] = 'test-user'
        cookies['first_name'] = 'Test'
        cookies['last_name'] = 'User'
        cookies['telephone'] = '1234'
        cookies['email'] = 'test-user@gmail.com'
        cookies['mobile'] = '1234'
        cookies['department'] = 'EP/DT'
        cookies['home_institute'] = 'TU'

    client.cookies = cookies
    return client

class ViewsTest(TestCase):
    """Test class experiments view."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
        'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpTestData(cls):
        """Ran once before all tests are run."""
        pass

    def test_index(self):
        """Tests index."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/index.html')

    def test_experiment_list(self):
        """Tests experiment list."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:experiments_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/experiments_list.html')
        self.assertTemplateUsed('samples_manager/partial_experiments_list.html')

    def test_admin_experiment_list(self):
        """Tests admin experiment list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:experiments_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/experiments_list.html')
        self.assertTemplateUsed('samples_manager/partial_admin_experiments_list.html')
    
    def test_experiment_sample_list(self):
        """Tests sample list."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:experiment_samples_list', args=[4]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/experiment_samples_list.html')
        self.assertTemplateUsed('samples_manager/partial_experiment_samples_list.html')

    def test_unauthorized_experiment_sample_list(self):
        """Tests sample list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:experiment_samples_list', args=[2]))

        self.assertEqual(response.status_code, 403)

    def test_experiment_user_list(self):
        """Tests user list."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:experiment_users_list', args=[4]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/experiment_users_list.html')
        self.assertTemplateUsed('samples_manager/partial_users_list.html')

    def test_unauthorized_experiment_user_list(self):
        """Tests user list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:experiment_users_list', args=[2]))

        self.assertEqual(response.status_code, 403)

    def test_irradiation_list(self):
        """Tests irradiation list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:irradiations_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/irradiations_list.html')
        self.assertTemplateUsed('samples_manager/partial_irradiations_list.html')

    def test_unauthorized_irradiation_list(self):
        """Tests irradiation list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:irradiations_list'))

        self.assertEqual(response.status_code, 403)

    def test_user_list(self):
        """Tests user list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:users_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/users_list.html')
        self.assertTemplateUsed('samples_manager/partial_users_list.html')

    def test_unauthorized_user_list(self):
        """Tests user list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:users_list'))

        self.assertEqual(response.status_code, 403)

    def test_compound_list(self):
        """Tests compound list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:compounds_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/compounds_list.html')
        self.assertTemplateUsed('samples_manager/partial_compounds_list.html')

    def test_unauthorized_compound_list(self):
        """Tests compound list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:compounds_list'))

        self.assertEqual(response.status_code, 403)

    def test_dosimeter_list(self):
        """Tests dosimeter list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:dosimeters_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/dosimeters_list.html')
        self.assertTemplateUsed('samples_manager/partial_dosimeters_list.html')

    def test_unauthorized_dosimeter_list(self):
        """Tests dosimeter list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:dosimeters_list'))

        self.assertEqual(response.status_code, 403)

    def test_box_list(self):
        """Tests box list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:boxes_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/boxes_list.html')
        self.assertTemplateUsed('samples_manager/partial_boxes_list.html')

    def test_unauthorized_box_list(self):
        """Tests box list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:boxes_list'))

        self.assertEqual(response.status_code, 403)

    def test_dosimetry_results_list(self):
        """Tests dosimetry result list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:dosimetry_results_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/dosimetry_results_list.html')
        self.assertTemplateUsed('samples_manager/partial_dosimetry_results_list.html')

    def test_unauthorized_dosimetry_results_list(self):
        """Tests dosimetry result list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:dosimetry_results_list'))

        self.assertEqual(response.status_code, 403)

    def test_fluence_factor_list(self):
        """Tests fluence factor list."""
        client = Client()
        set_user_cookies(client, 'Admin')
        response = client.get(reverse('samples_manager:fluence_factors_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('samples_manager/fluence_factor_list.html')
        self.assertTemplateUsed('samples_manager/partial_fluence_factors_list.html')

    def test_unauthorized_fluence_factor_list(self):
        """Tests fluence factor list access restriction."""
        client = Client()
        set_user_cookies(client, 'User')
        response = client.get(reverse('samples_manager:fluence_factors_list'))

        self.assertEqual(response.status_code, 403)
