import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urlparse, urljoin

# Fungsi untuk mengambil konten halaman web
def get_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Menghasilkan error jika status HTTP bukan 200
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses {url}: {e}")
        return None

# Fungsi untuk mengekstrak data SEO dari halaman web
def extract_seo_data(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Mengambil title
    title = soup.title.string if soup.title else 'N/A'
    
    # Mengambil meta description
    meta_desc = ''
    meta_tag_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_tag_desc and 'content' in meta_tag_desc.attrs:
        meta_desc = meta_tag_desc['content']
    
    # Mengambil meta keywords
    meta_keywords = ''
    meta_tag_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_tag_keywords and 'content' in meta_tag_keywords.attrs:
        meta_keywords = meta_tag_keywords['content']

    # Mengambil H1 tag (bisa ada lebih dari satu, ambil semua)
    h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]

    # Mengambil H2 tag (bisa ada lebih dari satu, ambil semua)
    h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
    
    # Mengambil konten utama (coba beberapa tag yang umum digunakan)
    main_content = ''
    article = soup.find('article')
    if article:
        main_content = ' '.join([p.get_text(strip=True) for p in article.find_all('p')])
    else:
        div_main = soup.find('div', {'class': 'main-content'})
        if div_main:
            main_content = ' '.join([p.get_text(strip=True) for p in div_main.find_all('p')])
        else:
            # Ambil semua paragraf jika tag artikel atau div utama tidak ditemukan
            main_content = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])

    # Mengambil link internal dan eksternal
    internal_links = []
    external_links = []
    domain = urlparse(url).netloc

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        parsed_href = urlparse(href)

        # Mengabaikan link tanpa skema (misal link mailto: atau javascript:void(0);)
        if not parsed_href.scheme:
            continue

        # Cek apakah link internal atau eksternal
        if parsed_href.netloc == domain or not parsed_href.netloc:  # Internal link
            full_url = urljoin(url, href)  # Buat URL penuh dari link relatif
            internal_links.append(full_url)
        else:  # External link
            external_links.append(href)

    return {
        'URL': url,
        'Title': title,
        'Meta Description': meta_desc,
        'Meta Keywords': meta_keywords,
        'H1 Tags': '; '.join(h1_tags),  # Gabungkan H1 tags dengan pemisah ";"
        'H2 Tags': '; '.join(h2_tags),  # Gabungkan H2 tags dengan pemisah ";"
        'Main Content': main_content[:500] + '...' if len(main_content) > 500 else main_content,  # Potong konten panjang
        'Internal Links': '; '.join(internal_links),  # Gabungkan internal link dengan pemisah ";"
        'External Links': '; '.join(external_links)   # Gabungkan external link dengan pemisah ";"
    }

# Fungsi utama untuk melakukan scraping SEO dari banyak URL
def scrape_seo_data(urls):
    seo_data_list = []
    
    for url in urls:
        print(f"Scraping {url}...")
        html_content = get_page_content(url)
        
        if html_content:
            seo_data = extract_seo_data(html_content, url)
            seo_data_list.append(seo_data)
        else:
            print(f"Gagal scrape {url}")
        
        time.sleep(random.uniform(1, 3))  # Random delay untuk menghindari deteksi bot
    
    return seo_data_list

# Fungsi untuk menyimpan hasil scraping ke file CSV
def save_to_csv(data, filename):
    if data:  # Pastikan ada data yang disimpan
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Data berhasil disimpan ke {filename}")
    else:
        print("Tidak ada data untuk disimpan.")

# Daftar URL yang akan di-scrape
urls = [
    'https://www.codepolitan.com/blog/siapa-bjorka-sebenarnya-hacker-di-balik-kebocoran-data-npwp/'
]

# Melakukan scraping untuk semua URL
seo_data = scrape_seo_data(urls)

# Menyimpan hasil scraping ke file CSV
save_to_csv(seo_data, 'seo_data_multiple_websites_with_keywords_h2.csv')
