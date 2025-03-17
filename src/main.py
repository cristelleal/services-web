import os
from dotenv import load_dotenv

from src.database import init_db, insert_article

def main():
    # Charge les variables d'environnement
    load_dotenv()

    # Initialise la base (création de table si besoin)
    init_db()

    

if __name__ == "__main__":
    main()
