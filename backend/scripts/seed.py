#!/usr/bin/env python
"""
Script para poblar la base de datos.
Uso: cd backend && python scripts/seed.py
Uso con limpieza: cd backend && python scripts/seed.py --force
"""

import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, Base, engine
from app.models.category import Category
from app.models.channel import Channel

# Slugs verificados desde tvtvhd.com/status.json
# Formato: (nombre, slug, categoria, activo)
CHANNELS = [
    # LATINOAMÉRICA
    ("ESPN",                        "espn",                   "deportes", True),
    ("ESPN 2",                      "espn2",                  "deportes", True),
    ("ESPN 3",                      "espn3",                  "deportes", True),
    ("ESPN 4",                      "espn4",                  "deportes", True),
    ("ESPN 5",                      "espn5",                  "deportes", True),
    ("ESPN 6",                      "espn6",                  "deportes", True),
    ("ESPN 7",                      "espn7",                  "deportes", True),
    ("DSports",                     "dsports",                "deportes", True),
    ("DSports 2",                   "dsports2",               "deportes", True),
    ("DSports Plus",                "dsportsplus",            "deportes", False),
    ("GOLTV",                       "goltv",                  "deportes", True),
    ("VTV Plus",                    "vtvplus",                "deportes", True),
    # ARGENTINA
    ("Fox Sports",                  "foxsports",              "deportes", True),
    ("Fox Sports 2",                "foxsports2",             "deportes", True),
    ("Fox Sports 3",                "foxsports3",             "deportes", True),
    ("TNT Sports",                  "tntsports",              "deportes", True),
    ("ESPN Premium",                "espnpremium",            "deportes", True),
    ("TyC Sports",                  "tycsports",              "deportes", True),
    ("TyC Sports Internacional",    "tycinternacional",       "deportes", True),
    ("Telefe",                      "telefe",                 "general",  True),
    ("TV Pública",                  "tvpublica",              "general",  False),
    # PERÚ
    ("GOLPERU",                     "golperu",                "deportes", True),
    ("Liga 1 MAX",                  "liga1max",               "deportes", True),
    ("Movistar Deportes",           "movistar",               "deportes", True),
    # COLOMBIA
    ("Win Sports Plus",             "winsportsplus",          "deportes", False),
    ("Win Sports Plus 2",           "winsports2",             "deportes", True),
    ("Win Sports",                  "winsports",              "deportes", False),
    # MÉXICO
    ("Fox Sports MX",               "foxsportsmx",            "deportes", True),
    ("Fox Sports 2 MX",             "foxsports2mx",           "deportes", True),
    ("Fox Sports 3 MX",             "foxsports3mx",           "deportes", True),
    ("Fox Sports Premium MX",       "foxsportspremium",       "deportes", True),
    ("ESPN MX",                     "espnmx",                 "deportes", True),
    ("ESPN 2 MX",                   "espn2mx",                "deportes", True),
    ("ESPN 3 MX",                   "espn3mx",                "deportes", True),
    ("ESPN 4 MX",                   "espn4mx",                "deportes", True),
    ("Azteca 7",                    "azteca7",                "general",  True),
    ("Canal 5",                     "canal5",                 "general",  True),
    ("Azteca Deportes",             "azteca_deportes",        "deportes", True),
    ("Caliente TV",                 "calientetv",             "deportes", False),
    # USA — béisbol MLB en español aquí
    ("TUDN",                        "tudn",                   "usa",      True),
    ("Fox Deportes",                "foxdeportes",            "usa",      True),
    ("ESPN Deportes",               "espndeportes",           "usa",      True),
    ("Unimás",                      "unimas",                 "usa",      True),
    ("BeIN Sports Español",         "beinsportes",            "usa",      True),
    ("BeIN Sports Xtra Español",    "beinsport_xtra_espanol", "usa",      True),
    ("USA Network",                 "usanetwork",             "usa",      True),
    ("Telemundo",                   "telemundo",              "usa",      True),
    # BRASIL
    ("Sportv",                      "sportv",                 "brasil",   True),
    ("Sportv 2",                    "sportv2",                "brasil",   True),
    ("Sportv 3",                    "sportv3",                "brasil",   True),
    ("Premiere 1",                  "premiere1",              "brasil",   True),
    ("Premiere 2",                  "premiere2",              "brasil",   True),
    # MUNDIAL
    ("ESPN NL",                     "espn1_nl",               "deportes", True),
    ("ESPN 2 NL",                   "espn2_nl",               "deportes", True),
    ("ESPN 3 NL",                   "espn3_nl",               "deportes", True),
    # ESPAÑA (actualmente inactivos pero disponibles)
    ("DAZN 1",                      "dazn1",                  "deportes", False),
    ("DAZN 2",                      "dazn2",                  "deportes", False),
    ("DAZN 3",                      "dazn3",                  "deportes", False),
    ("DAZN 4",                      "dazn4",                  "deportes", False),
    ("DAZN LaLiga",                 "dazn_laliga",            "deportes", False),
    ("Liga de Campeones 1",         "ligadecampeones1",       "deportes", False),
    ("Liga de Campeones 2",         "ligadecampeones2",       "deportes", False),
    ("Liga de Campeones 3",         "ligadecampeones3",       "deportes", False),
]


def seed(force=False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if force:
        print("Limpiando datos existentes...")
        db.query(Channel).delete()
        db.query(Category).delete()
        db.commit()
    else:
        if db.query(Category).count() > 0:
            print("La BD ya tiene datos. Usa --force para reemplazar.")
            db.close()
            return

    categories = [
        Category(name="Deportes",  slug="deportes", icon="fa-futbol"),
        Category(name="USA",       slug="usa",      icon="fa-flag"),
        Category(name="Brasil",    slug="brasil",   icon="fa-futbol"),
        Category(name="General",   slug="general",  icon="fa-tv"),
    ]
    db.add_all(categories)
    db.flush()
    cat_map = {c.slug: c.id for c in categories}

    channels = []
    for name, slug, cat_slug, active in CHANNELS:
        channels.append(Channel(
            name=name,
            slug=slug,
            stream_url=f"https://tvtvhd.com/vivo/canales.php?stream={slug}",
            category_id=cat_map[cat_slug],
            is_active=active,
        ))

    db.add_all(channels)
    db.commit()
    print(f"Seed completado: {len(categories)} categorias, {len(channels)} canales.")
    db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
