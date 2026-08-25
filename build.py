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
HOME_FILE = PAGES_DIR / "home.html"


# ============================================================
# UTILITAIRES
# ============================================================

def read_text(path):
    return path.read_text(encoding="utf-8")


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def render_template(template, variables):
    """
    Remplace les variables de type :

        {{variable}}

    par les valeurs contenues dans le dictionnaire variables.
    """

    pattern = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

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
    Vérifie qu'aucune variable {{...}} n'est restée
    dans le HTML généré.
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
# GÉNÉRATION DE LA HOMEPAGE
# ============================================================

def build_home(language):
    print(f"Construction de la Homepage [{language.upper()}]...")

    # --------------------------------------------------------
    # Chargement des fichiers sources
    # --------------------------------------------------------

    layout_template = read_text(LAYOUT_FILE)
    header_template = read_text(HEADER_FILE)
    home_template = read_text(HOME_FILE)

    locale_file = LOCALES_DIR / f"{language}.json"
    locale = load_json(locale_file)


    # --------------------------------------------------------
    # Variables propres à la Homepage
    # --------------------------------------------------------

    variables = dict(locale)

    variables.update({
        # Depuis /fr/index.html ou /en/index.html
        # les ressources communes se trouvent un niveau plus haut.
        "root_path": "../",

        # Navigation
        "home_url": "index.html",
        "dual_mode_url": "#dual-mode",

        # Changement de langue
        "fr_url": "../fr/index.html",
        "en_url": "../en/index.html",
    })


    # --------------------------------------------------------
    # État du sélecteur de langue
    # --------------------------------------------------------

    if language == "fr":
        variables.update({
            "fr_active_class": "is-active",
            "en_active_class": "",

            "fr_aria_current": 'aria-current="page"',
            "en_aria_current": "",
        })

    elif language == "en":
        variables.update({
            "fr_active_class": "",
            "en_active_class": "is-active",

            "fr_aria_current": "",
            "en_aria_current": 'aria-current="page"',
        })

    else:
        raise ValueError(
            f"Langue non prise en charge : {language}"
        )


    # --------------------------------------------------------
    # Homepage active dans la navigation
    # --------------------------------------------------------

    variables["home_aria_current"] = 'aria-current="page"'


    # --------------------------------------------------------
    # Génération du header
    # --------------------------------------------------------

    rendered_header = render_template(
        header_template,
        variables
    )


    # --------------------------------------------------------
    # Génération du contenu de la Homepage
    # --------------------------------------------------------

    rendered_home = render_template(
        home_template,
        variables
    )


    # --------------------------------------------------------
    # Injection dans le layout général
    # --------------------------------------------------------

    page_variables = dict(variables)

    page_variables.update({
        "header": rendered_header,
        "content": rendered_home,
    })

    final_html = render_template(
        layout_template,
        page_variables
    )


    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    check_unresolved_variables(final_html)


    # --------------------------------------------------------
    # Dossier de destination
    # --------------------------------------------------------

    output_dir = BASE_DIR / language

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_dir / "index.html"


    # --------------------------------------------------------
    # Écriture
    # --------------------------------------------------------

    output_file.write_text(
        final_html,
        encoding="utf-8"
    )

    print(
        f"OK : {output_file.relative_to(BASE_DIR)}"
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

    build_home("fr")
    build_home("en")

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