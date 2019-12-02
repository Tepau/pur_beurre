from off.thetest import OpenFoodFacts
from off.models import Category, Product

liste_categories = [ 'Produits à tartiner', 'Petit-déjeuners', 'Produits à tartiner sucrés', 'Pâtes à tartiner',
                     'Pâtes à tartiner aux noisettes', 'Pâtes à tartiner au chocolat',
                     'Pâtes à tartiner aux noisettes et au cacao' ]

produits = OpenFoodFacts(liste_categories).get_selected_product()

for categorie in liste_categories:
    Category.objects.create(name=categorie)

for produit in produits:
    element = Product.objects.create(name=produit[1].lower(), nutriscore=produit[0], url_image=produit[3], url_link=produit[4])
    for cat in produit[2]:
        element.category.add(Category.objects.get(name=cat))
        element.save()

