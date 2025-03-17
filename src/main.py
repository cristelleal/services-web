import os
from dotenv import load_dotenv

from src.database import init_db, insert_article
from src.rss_reader import scrape_rss_feed
from src.scraper import fetch_page, extract_title, search_google
from src.cleaning import clean_html

def main():
    # Charge les variables d'environnement
    load_dotenv()

    # Initialise la base (création de table si besoin)
    init_db()

    # 1) Scraping via RSS
    rss_feeds = [
        # "https://www.sciencedaily.com/rss/matter_energy/quantum_computing.xml",
        "https://lejournal.cnrs.fr/rss/5071"
    ]

    for feed_url in rss_feeds:
        articles = scrape_rss_feed(feed_url)
        for article in articles:
            link = article["link"]
            html_content = fetch_page(link)
            if html_content:
                # Nettoyage du contenu
                cleaned_text = clean_html(html_content)
                # Extraction d'un titre plus précis (ou fallback sur celui du RSS)
                real_title = extract_title(html_content) or article["title"]

                insert_article(
                    title=real_title,
                    link=link,
                    content=cleaned_text,
                    publication_date=article["publication_date"],
                    source=feed_url
                )
                print(f"[RSS] Article inséré : {real_title}")

    # 2) Recherche via Google (optionnel)
    google_results = search_google("quantum cryptography news", num_results=5)
    for result in google_results:
        link = result["link"]
        html_content = fetch_page(link)
        if html_content:
            cleaned_text = clean_html(html_content)
            real_title = extract_title(html_content) or result["title"]

            insert_article(
                title=real_title,
                link=link,
                content=cleaned_text,
                publication_date=None,
                source="GoogleSearch"
            )
            print(f"[Google] Article inséré : {real_title}")

if __name__ == "__main__":
    main()
