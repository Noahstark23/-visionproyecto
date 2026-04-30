#!/usr/bin/env python
"""
Script para poblar la base de datos con datos iniciales.
Uso: cd backend && python scripts/seed.py
Uso con limpieza: cd backend && python scripts/seed.py --force
"""

import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, Base, engine
from app.models.category import Category
from app.models.channel import Channel

CHANNELS = [
    # ESPN
    ("ESPN",                      "espnmx",                 "deportes"),
    ("ESPN 2",                    "espn2mx",                "deportes"),
    ("ESPN 3",                    "espn3mx",                "deportes"),
    ("ESPN 4",                    "espn4mx",                "deportes"),
    ("ESPN 5",                    "espn5",                  "deportes"),
    ("ESPN 6",                    "espn6",                  "deportes"),
    ("ESPN 7",                    "espn7",                  "deportes"),
    ("ESPN Premium",              "espnpremium",            "deportes"),
    # Fox Sports
    ("Fox Sports",                "foxsports",              "deportes"),
    ("Fox Sports MX",             "foxsportsmx",            "deportes"),
    ("Fox Sports 2",              "foxsports2mx",           "deportes"),
    ("Fox Sports 3",              "foxsports3mx",           "deportes"),
    # DSports
    ("DSports",                   "dsports",                "deportes"),
    ("DSports 2",                 "dsports2",               "deportes"),
    ("DSports Plus",              "dsportsplus",            "deportes"),
    ("DSports 2 Alt",             "dsports2_1",             "deportes"),
    ("DSports Plus Alt",          "dsportsplus_1",          "deportes"),
    # TyC / TNT
    ("TyC Sports",                "tycsports",              "deportes"),
    ("TyC Sports Internacional",  "tycinternacional",       "deportes"),
    ("TNT Sports",                "tntsports",              "deportes"),
    # BeIN / CBS / Caliente
    ("BeIN Sports Español",       "beinsports_spanish",     "deportes"),
    ("BeIN Sports Xtra",          "beinsports_xtra_spanish","deportes"),
    ("CBS Sports Network",        "cbssports",              "deportes"),
    ("Caliente TV",               "calientetv",             "deportes"),
    # Win Sports
    ("Win Sports Plus",           "winsportsplus",          "deportes"),
    ("Win Sports Plus 2",         "winsports2",             "deportes"),
    # Liga / Movistar / GO / VTV
    ("Liga 1 MAX",                "liga1max",               "deportes"),
    ("Movistar Deportes",         "movistar",               "deportes"),
    ("GO",                        "golperu",                "deportes"),
    ("VTV Plus",                  "vtvplus",                "deportes"),
    # DAZN
    ("DAZN 1",                    "dazn1",                  "deportes"),
    ("DAZN 1 DE",                 "dazn1de",                "deportes"),
    ("DAZN 2",                    "dazn2",                  "deportes"),
    ("DAZN 2 DE",                 "dazn2de",                "deportes"),
    ("DAZN 3",                    "dazn3",                  "deportes"),
    ("DAZN 4",                    "dazn4",                  "deportes"),
    ("DAZN LaLiga",               "dazn_laliga",            "deportes"),
    ("Dazn Eleven 1",             "dazn_eleven1",           "deportes"),
    ("Dazn Eleven 2",             "dazn_eleven2",           "deportes"),
    ("Dazn Eleven 3",             "dazn_eleven3",           "deportes"),
    ("Dazn Eleven 4",             "dazn_eleven4",           "deportes"),
    ("Dazn Eleven 5",             "dazn_eleven5",           "deportes"),
    # Azteca
    ("Azteca 7",                  "azteca7",                "general"),
    ("Azteca Deportes",           "aztecadeportes",         "deportes"),
    # General
    ("Canal 5",                   "canal5",                 "general"),
    ("Canal 11",                  "canal11",                "general"),
    ("Telefe",                    "telefe",                 "general"),
    ("TV Pública",                "tvpublica",              "general"),
]

def seed(force=False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if force:
        print("🗑️  Limpiando datos existentes...")
        db.query(Channel).delete()
        db.query(Category).delete()
        db.commit()
    else:
        existing = db.query(Category).count()
        if existing > 0:
            print("⚠️  La BD ya tiene datos. Usa --force para reemplazar.")
            db.close()
            return

    categories = [
        Category(name="Deportes",     slug="deportes",     icon="fa-futbol"),
        Category(name="General",      slug="general",      icon="fa-tv"),
    ]
    db.add_all(categories)
    db.flush()
    db.refresh(categories[0])
    db.refresh(categories[1])

    cat_map = {c.slug: c.id for c in categories}

    channels = []
    for name, slug, cat_slug in CHANNELS:
        stream_url = f"https://tvtvhd.com/vivo/canales.php?stream={slug}"
        channels.append(Channel(
            name=name,
            slug=slug,
            stream_url=stream_url,
            category_id=cat_map[cat_slug],
            is_active=True,
        ))

    db.add_all(channels)
    db.commit()

    print("✅ Seed completado!")
    print(f"   - Categorías: {len(categories)}")
    print(f"   - Canales: {len(channels)}")
    db.close()

if __name__ == "__main__":
    force = "--force" in sys.argv
    seed(force=force)
