from pathlib import Path
import json
import re


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR / "src"
PAGES_DIR = SRC_DIR / "pages"
COMPONENTS_DIR = SRC_DIR / "components"
LOCALES_DIR = SRC_DIR / "locales"

LAYOUT_FILE = SRC_DIR / "layout.html"
HEADER_FILE = COMPONENTS_DIR / "header.html"


# Pages du portfolio
PAGES = {
    "home": {
        "template": "home.html",
        "output": "",
    },

    "admin-sys": {
        "template": "admin-sys.html",
        "output": "admin-sys",
    },
}


# Langues disponibles
LANGUAGES = ("fr", "en")


# ============================================================
# UTILITAIRES
# ============================================================

def read_text(path):
    return path.read_text(encoding="utf-8")


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def merge_dicts(*dictionaries):
    """
    Fusionne plusieurs dictionnaires.

    Les valeurs des dictionnaires placés à droite
    remplacent celles portant le même nom à gauche.
    """

    result = {}

    for dictionary in dictionaries:
        result.update(dictionary)

    return result


def render_template(template, variables):
    """
    Remplace :

        {{variable}}

    par la valeur correspondante.
    """

    pattern = re.compile(
        r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}"
    )

    def replace(match):
        key = match.group(1)

        if key not in variables:
            raise KeyError(
                f"Variable manquante dans le template : {key}"
            )

        return str(variables[key])

    return pattern.sub(replace, template)


def check_unresolved_variables(content):
    """
    Vérifie qu'aucune variable {{...}}
    ne reste dans le HTML généré.
    """

    unresolved = re.findall(
        r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}",
        content
    )

    if unresolved:
        raise ValueError(
            "Variables non remplacées : "
            + ", ".join(sorted(set(unresolved)))
        )


# ============================================================
# CHARGEMENT DES TRADUCTIONS
# ============================================================

def load_locale(language, page_name):

    common_file = (
        LOCALES_DIR
        / language
        / "common.json"
    )

    page_file = (
        LOCALES_DIR
        / language
        / f"{page_name}.json"
    )


    if not common_file.exists():
        raise FileNotFoundError(
            f"Fichier commun introuvable : {common_file}"
        )


    if not page_file.exists():
        raise FileNotFoundError(
            f"Fichier de page introuvable : {page_file}"
        )


    common_data = load_json(common_file)
    page_data = load_json(page_file)


    return merge_dicts(
        common_data,
        page_data
    )


# ============================================================
# CHEMINS DES PAGES
# ============================================================

def get_page_paths(language, page_name):

    if page_name == "home":

        return {
            "root_path": "../",

            "home_url": "index.html",

            "dual_mode_url": "#dual-mode",
            
            "admin_page_url": "admin-sys/index.html",

            "fr_url": "../fr/index.html",

            "en_url": "../en/index.html",

            "home_aria_current": 'aria-current="page"',
        }


    if page_name == "admin-sys":

        return {
            "root_path": "../../",

            "home_url": "../index.html",

            "dual_mode_url": "../index.html#dual-mode",

            "fr_url": "../../fr/admin-sys/index.html",

            "en_url": "../../en/admin-sys/index.html",

            "home_aria_current": "",
        }


    raise ValueError(
        f"Configuration de chemins absente pour : {page_name}"
    )


# ============================================================
# ÉTAT DU SÉLECTEUR DE LANGUE
# ============================================================

def get_language_state(language):

    if language == "fr":

        return {
            "fr_active_class": "is-active",
            "en_active_class": "",

            "fr_aria_current": 'aria-current="page"',
            "en_aria_current": "",
        }


    if language == "en":

        return {
            "fr_active_class": "",
            "en_active_class": "is-active",

            "fr_aria_current": "",
            "en_aria_current": 'aria-current="page"',
        }


    raise ValueError(
        f"Langue non prise en charge : {language}"
    )


# ============================================================
# DESTINATION
# ============================================================

def get_output_file(language, page_name):

    page_config = PAGES[page_name]

    output_part = page_config["output"]


    # Homepage
    if output_part == "":

        output_dir = BASE_DIR / language


    # Pages internes
    else:

        output_dir = (
            BASE_DIR
            / language
            / output_part
        )


    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    return output_dir / "index.html"


# ============================================================
# GÉNÉRATION D'UNE PAGE
# ============================================================

def build_page(language, page_name):

    print(
        f"Construction : "
        f"{page_name} [{language.upper()}]..."
    )


    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    layout_template = read_text(
        LAYOUT_FILE
    )

    header_template = read_text(
        HEADER_FILE
    )


    page_config = PAGES[page_name]

    page_template_file = (
        PAGES_DIR
        / page_config["template"]
    )


    if not page_template_file.exists():
        raise FileNotFoundError(
            f"Template introuvable : "
            f"{page_template_file}"
        )


    page_template = read_text(
        page_template_file
    )


    # --------------------------------------------------------
    # Traductions
    # --------------------------------------------------------

    locale_variables = load_locale(
        language,
        page_name
    )


    # --------------------------------------------------------
    # Variables générales
    # --------------------------------------------------------

    path_variables = get_page_paths(
        language,
        page_name
    )

    language_variables = get_language_state(
        language
    )


    variables = merge_dicts(
        locale_variables,
        path_variables,
        language_variables
    )


    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    rendered_header = render_template(
        header_template,
        variables
    )


    # --------------------------------------------------------
    # Contenu de la page
    # --------------------------------------------------------

    rendered_content = render_template(
        page_template,
        variables
    )


    # --------------------------------------------------------
    # Layout final
    # --------------------------------------------------------

    final_variables = dict(variables)

    final_variables.update({
        "header": rendered_header,
        "content": rendered_content,
    })


    final_html = render_template(
        layout_template,
        final_variables
    )


    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    check_unresolved_variables(
        final_html
    )


    # --------------------------------------------------------
    # Destination
    # --------------------------------------------------------

    output_file = get_output_file(
        language,
        page_name
    )


    # --------------------------------------------------------
    # Écriture
    # --------------------------------------------------------

    output_file.write_text(
        final_html,
        encoding="utf-8"
    )


    print(
        f"OK : "
        f"{output_file.relative_to(BASE_DIR)}"
    )


# ============================================================
# BUILD COMPLET
# ============================================================

def build():

    print()
    print("========================================")
    print("       BLACKBIRD STATIC BUILDER")
    print("========================================")
    print()


    for language in LANGUAGES:

        for page_name in PAGES:

            build_page(
                language,
                page_name
            )


    print()
    print("========================================")
    print("Build terminé avec succès.")
    print("========================================")
    print()


# ============================================================
# POINT D'ENTRÉE
# ============================================================

if __name__ == "__main__":
    build()