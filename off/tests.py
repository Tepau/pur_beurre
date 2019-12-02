from django.test import TestCase
from django.urls import reverse
from .models import Product, Category
from django.contrib.auth.models import User
from django.test import Client


class HomePageTestCase(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class ArticlePageTestCase(TestCase):

    def setUp(self):
        product_a = Produit.objects.create(nutriscore="a", name='test_a', url_image='image_a', url_link='url_a')
        product_b = Produit.objects.create(nutriscore="b", name='test_b', url_image='image_b', url_link='url_b')
        category = Categorie.objects.create(name="categorie")
        product_a.categorie.add(Categorie.objects.get(name='categorie'))
        product_b.categorie.add(Categorie.objects.get(name='categorie'))
        self.product_a = Produit.objects.get(name='test_a')
        self.product_b = Produit.objects.get(name='test_b')
        self.client = Client()
        user = User.objects.create_user('test', 'test@email.com', 'password')
        self.nb_product = user.produit_set.count()

    def test_article_page_returns_200(self):
        product_name = self.product_a.nom
        response = self.client.get(reverse('off:article', args=(product_name,)))
        self.assertEqual(response.status_code, 200)

    def test_print_product_with_best_nutriscore(self):
        product_name = self.product_b.nom
        response = self.client.get(reverse('off:article', args=(product_name,)))
        self.assertContains(response, self.product_a.nom.capitalize())

    def test_not_print_product_with_bad_nutriscore(self):
        product_name = self.product_a.nom
        response = self.client.get(reverse('off:article', args=(product_name,)))
        self.assertNotContains(response, self.product_b.nom.capitalize())

    def test_print_form_if_user_is_connect(self):
        self.client.login(username='test', password='password')
        product_name_a = self.product_a.nom
        product_name_b = self.product_b.nom
        response = self.client.get(reverse('off:article', args=(product_name_b,)))
        self.assertContains(response, 'Sauvegarder')

    def test_not_print_form_if_user_is_not_connect(self):
        product_name_b = self.product_b.nom
        response = self.client.get(reverse('off:article', args=(product_name_b,)))
        self.assertNotContains(response, 'Sauvegarder')

    def test_save_product(self):
        self.client.login(username='test', password='password')
        user = User.objects.get(username='test')
        data = {'id_produit': self.product_a.id}
        product_name_b = self.product_b.nom
        response = self.client.post(reverse('off:article', args=(product_name_b,)), data)
        new_nb_product = user.produit_set.count()
        self.assertEqual(new_nb_product, self.nb_product + 1)

    def test_article_page_returns_404(self):
        fake_product = 'fake_product'
        response = self.client.get(reverse('off:article', args=(fake_product,)))
        self.assertEqual(response.status_code, 404)

    def test_article_page_return_sentence_if_no_bette_product(self):
        product_name = self.product_a.nom
        response = self.client.get(reverse('off:article', args=(product_name,)))
        self.assertContains(response, "aucun produit")


class InscriptionPageTestCase(TestCase):

    def setUp(self):
        self.nb_user = User.objects.count()

    def new_user_is_registred(self):

        data = {'pseudo': 'nametest', 'email': 'emailtest@email.com', 'password': 'passwordtest'}
        response = self.client.post(reverse('off:registration'), data)
        new_nb_user = User.objects.count()
        self.assertEqual(new_nb_user, self.nb_user + 1)


class LoginPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('test', 'test@email.com', 'passwordtest')

    def testLogin(self):
        self.client.login(username='test', password='passwordtest')
        response = self.client.get(reverse('off:registration'))
        self.assertEqual(response.status_code, 200)



class MentionsPageTestCase(TestCase):
    def test_mentions_page(self):
        response = self.client.get(reverse('off:mentions'))
        self.assertEqual(response.status_code, 200)


class AccountPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='utilisateur', password='mot_de_passe', email='test@test.com')

    def test_page_return_200_if_connect(self):
        self.client.login(username='utilisateur', password='mot_de_passe')
        response = self.client.get(reverse('off:account'))
        self.assertEqual(response.status_code, 200)

    def test_page_return_302_if_not_connect(self):
        response = self.client.get(reverse('off:account'))
        self.assertEqual(response.status_code, 302)


class MyProductsPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='utilisateur', password='mot_de_passe', email='test@test.com')

    def test_page_return_200_if_connect(self):
        self.client.login(username='utilisateur', password='mot_de_passe')
        response = self.client.get(reverse('off:my_products'))
        self.assertEqual(response.status_code, 200)

    def test_page_return_302_if_not_connect(self):
        response = self.client.get(reverse('off:my_products'))
        self.assertEqual(response.status_code, 302)
