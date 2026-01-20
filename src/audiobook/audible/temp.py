def _fetch_api(self):
    # On initialise le client sans authentification
    # On précise juste le pays pour taper sur le bon catalogue
    # client = audible.Client(region="fr")

    # # Récupération des détails publics du livre
    # book_details = client.get(f"catalog/products/{self._args.asin}")

    # # Extraction de l'URL de l'image
    # cover_url = book_details["product"]["item_links"]["content_metadata"][
    #     "content_reference"
    # ]["image_url"]
    # print(f"URL de la cover : {cover_url}")
    auth = audible.Authenticator()

    # 2. On passe l'auth ET le country_code au Client
    # Le country_code est crucial ici pour définir la région (fr, us, etc.)
    client = audible.Client(auth=auth, country_code="fr")

    asin = "B017VFP93U"

    try:
        # Utilisation du point de terminaison du catalogue public
        response = client.get(f"catalog/products/{asin}")

        # Structure de la réponse pour l'image
        product = response.get("product", {})
        image_url = product.get("image_url")

        print(f"URL de la pochette : {image_url}")

    except Exception as e:
        print(f"Erreur : {e}")


def _download_cover(self, asin: str, output_dir: str = "covers"):
    # URL haute définition utilisée par le store Amazon/Audible
    url = f"https://m.media-amazon.com/images/I/{asin}._SL500_.jpg"
    print(url)

    Path(output_dir).mkdir(exist_ok=True)
    file_path = Path(output_dir) / f"{asin}.jpg"

    with httpx.Client() as client:
        response = client.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            return str(file_path)
    return None


def _fetch_metadata_public(self, asin: str):
    url = f"https://www.audible.fr/pd/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    with httpx.Client(headers=headers, follow_redirects=True) as client:
        resp = client.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # On cherche l'image principale dans le DOM
            img_tag = soup.find("img", class_="bc-pub-block")
            if img_tag:
                return img_tag["src"]

        print(resp.status_code)
    return None


def _upscale_audible_url(self, url: str, size: int = 500) -> str:
    """
    Transforme une URL de vignette Audible en URL haute résolution.
    Ex: ..._SL63_.jpg -> ..._SL500_.jpg
    """

    # On cherche le motif _SLxxx_ et on le remplace par la taille choisie
    # Cela fonctionne même si l'URL d'origine a une autre valeur que 63
    new_url = re.sub(r"_SL\d+_", f"_SL{size}_", url)
    return new_url


def _download_audible_cover(self, url: str, asin: str, output_folder: str = "covers"):
    # 1. Préparer le dossier de destination
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)

    # 2. Définir le chemin du fichier (ex: covers/B08N5N6V96.jpg)
    file_path = folder / f"{asin}.jpg"

    # 3. Télécharger et sauvegarder
    try:
        with httpx.Client() as client:
            response = client.get(url)
            # On vérifie si la requête a réussi (200 OK)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(response.content)

        print(f"✅ Image sauvegardée avec succès : {file_path}")
        return file_path

    except httpx.HTTPStatusError as e:
        print(f"❌ Erreur HTTP : {e.response.status_code}")
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")
    return None


def _get_audible_metadata(self, asin: str, locale: str = "fr"):
    url = f"https://www.audible.{locale}/pd/{asin}"
    # User-Agent est CRUCIAL : sans lui, Amazon bloque la requête
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=10) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return None

            print(url)
            soup = BeautifulSoup(resp.text, "html.parser")

            scripts = soup.find_all("script", type="application/ld+json")

            data = None
            for s in scripts:
                try:
                    temp_data = json.loads(s.string)
                    print(temp_data)
                    # On cherche celle qui décrit un produit (le livre)
                    if isinstance(temp_data, list):
                        temp_data = temp_data[0]

                    if temp_data.get("@type") in ["Product", "Book", "Audiobook"]:
                        data = temp_data
                        break
                except (json.JSONDecodeError, TypeError):
                    continue

            print(data)

            # --- MÉTHODE 2 : FALLBACK (Si le JSON est absent ou corrompu) ---
            # On cherche les éléments par leurs classes CSS Audible
            title = soup.find("h1")
            # author_list = soup.find("li", class_="authorLabel")
            print(title)

    except Exception as e:
        print(f"Erreur lors du fetch : {e}")

    return None
