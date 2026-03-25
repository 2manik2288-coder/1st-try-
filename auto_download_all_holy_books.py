# ============================================================
#   PRAMAN.AI — FAST Holy Books Downloader
#   Downloads 10 books SIMULTANEOUSLY — 10x faster
#   ALL Languages + ALL Versions + ALL Volumes
#   Run: python3 auto_download_all_holy_books.py
# ============================================================

import requests
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

SAVE_FOLDER   = "./holy_books_pdfs"
TRACKER_FILE  = "./download_tracker.txt"
FAILED_FILE   = "./failed_downloads.txt"
WORKERS       = 20      # Download 20 books at the same time
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Thread-safe lock for writing to tracker/counter
lock = threading.Lock()
downloaded_count = [0]
skipped_count    = [0]
failed_count     = [0]

SEARCH_QUERIES = [
    # ── HINDUISM ──
    ("Rigveda Sanskrit complete",                    "Hinduism"),
    ("Rigveda Hindi translation",                    "Hinduism"),
    ("Rigveda English Griffith translation",         "Hinduism"),
    ("Rigveda English Wilson translation",           "Hinduism"),
    ("Rigveda Tamil translation",                    "Hinduism"),
    ("Rigveda Telugu translation",                   "Hinduism"),
    ("Rigveda Bengali translation",                  "Hinduism"),
    ("Samaveda Sanskrit original",                   "Hinduism"),
    ("Samaveda Hindi translation",                   "Hinduism"),
    ("Samaveda English translation",                 "Hinduism"),
    ("Yajurveda Sanskrit complete",                  "Hinduism"),
    ("Yajurveda Hindi translation",                  "Hinduism"),
    ("Yajurveda English translation",                "Hinduism"),
    ("Shukla Yajurveda Sanskrit",                    "Hinduism"),
    ("Krishna Yajurveda Taittiriya",                 "Hinduism"),
    ("Atharvaveda Sanskrit complete",                "Hinduism"),
    ("Atharvaveda Hindi translation",                "Hinduism"),
    ("Atharvaveda English translation",              "Hinduism"),
    ("108 Upanishads Sanskrit",                      "Hinduism"),
    ("108 Upanishads Hindi",                         "Hinduism"),
    ("108 Upanishads English",                       "Hinduism"),
    ("Brihadaranyaka Upanishad Sanskrit",            "Hinduism"),
    ("Brihadaranyaka Upanishad Hindi",               "Hinduism"),
    ("Brihadaranyaka Upanishad English",             "Hinduism"),
    ("Chandogya Upanishad Sanskrit Hindi English",   "Hinduism"),
    ("Katha Upanishad Sanskrit Hindi English",       "Hinduism"),
    ("Principal Upanishads Radhakrishnan",           "Hinduism"),
    ("Upanishads Tamil translation",                 "Hinduism"),
    ("Upanishads Telugu translation",                "Hinduism"),
    ("Bhagavad Gita Sanskrit original",              "Hinduism"),
    ("Bhagavad Gita Hindi Geeta Press",              "Hinduism"),
    ("Bhagavad Gita English Prabhupada",             "Hinduism"),
    ("Bhagavad Gita English Radhakrishnan",          "Hinduism"),
    ("Bhagavad Gita English Annie Besant",           "Hinduism"),
    ("Bhagavad Gita English Tilak",                  "Hinduism"),
    ("Bhagavad Gita Urdu translation",               "Hinduism"),
    ("Bhagavad Gita Tamil",                          "Hinduism"),
    ("Bhagavad Gita Telugu",                         "Hinduism"),
    ("Bhagavad Gita Bengali",                        "Hinduism"),
    ("Bhagavad Gita Gujarati",                       "Hinduism"),
    ("Bhagavad Gita Marathi",                        "Hinduism"),
    ("Bhagavad Gita Kannada",                        "Hinduism"),
    ("Bhagavad Gita Malayalam",                      "Hinduism"),
    ("Bhagavad Gita Punjabi",                        "Hinduism"),
    ("Bhagavad Gita Spanish",                        "Hinduism"),
    ("Bhagavad Gita German",                         "Hinduism"),
    ("Bhagavad Gita French",                         "Hinduism"),
    ("Mahabharata Sanskrit complete",                "Hinduism"),
    ("Mahabharata Hindi complete",                   "Hinduism"),
    ("Mahabharata English Ganguli vol 1",            "Hinduism"),
    ("Mahabharata English Ganguli vol 2",            "Hinduism"),
    ("Mahabharata English Ganguli vol 3",            "Hinduism"),
    ("Mahabharata English Ganguli vol 4",            "Hinduism"),
    ("Mahabharata English Ganguli vol 5",            "Hinduism"),
    ("Mahabharata Tamil translation",                "Hinduism"),
    ("Mahabharata Telugu translation",               "Hinduism"),
    ("Mahabharata Bengali translation",              "Hinduism"),
    ("Valmiki Ramayana Sanskrit",                    "Hinduism"),
    ("Valmiki Ramayana Hindi",                       "Hinduism"),
    ("Valmiki Ramayana English Griffith",            "Hinduism"),
    ("Valmiki Ramayana English Dutt",                "Hinduism"),
    ("Ramcharitmanas Hindi Tulsidas",                "Hinduism"),
    ("Kamba Ramayanam Tamil",                        "Hinduism"),
    ("Ramayana Telugu translation",                  "Hinduism"),
    ("Ramayana Bengali Krittibasi",                  "Hinduism"),
    ("Bhagavata Purana Sanskrit",                    "Hinduism"),
    ("Bhagavata Purana Hindi",                       "Hinduism"),
    ("Bhagavata Purana English",                     "Hinduism"),
    ("Bhagavata Purana Tamil",                       "Hinduism"),
    ("Vishnu Purana Sanskrit Hindi English",         "Hinduism"),
    ("Shiva Purana Hindi English",                   "Hinduism"),
    ("Brahma Purana Sanskrit English",               "Hinduism"),
    ("Devi Bhagavata Purana Hindi",                  "Hinduism"),
    ("Markandeya Purana English",                    "Hinduism"),
    ("Garuda Purana Hindi English",                  "Hinduism"),
    ("Agni Purana Sanskrit English",                 "Hinduism"),
    ("Narada Purana Sanskrit English",               "Hinduism"),
    ("Padma Purana Sanskrit English",                "Hinduism"),
    ("Kurma Purana Sanskrit English",                "Hinduism"),
    ("Matsya Purana Sanskrit English",               "Hinduism"),
    ("Linga Purana Sanskrit English",                "Hinduism"),
    ("Skanda Purana Sanskrit English vol 1",         "Hinduism"),
    ("Skanda Purana Sanskrit English vol 2",         "Hinduism"),
    ("Brahmanda Purana Sanskrit English",            "Hinduism"),
    ("Yoga Sutras Patanjali Sanskrit Hindi English", "Hinduism"),
    ("Manusmriti Sanskrit Hindi English",            "Hinduism"),
    ("Arthashastra Kautilya Sanskrit English",       "Hinduism"),
    ("Chanakya Neeti Hindi Sanskrit",                "Hinduism"),
    ("Brahma Sutras Shankaracharya English",         "Hinduism"),
    ("Vivekachudamani Sanskrit Hindi English",       "Hinduism"),
    ("Ashtavakra Gita Sanskrit Hindi English",       "Hinduism"),
    ("Devi Mahatmya Durga Saptashati Hindi",         "Hinduism"),
    ("Swami Vivekananda complete works",             "Hinduism"),
    ("Thirukkural Tamil English",                    "Hinduism"),
    ("Tirumantiram Tamil",                           "Hinduism"),
    ("Divya Prabandham Tamil Alvars",                "Hinduism"),
    ("Harivamsa Sanskrit Hindi English",             "Hinduism"),
    ("Narada Bhakti Sutras Sanskrit English",        "Hinduism"),
    ("Ramakrishna Gospel English",                   "Hinduism"),

    # ── ISLAM ──
    ("Quran Arabic original",                        "Islam"),
    ("Quran Hindi translation",                      "Islam"),
    ("Quran Urdu Fateh Muhammad Jalandhari",         "Islam"),
    ("Quran Urdu Mufti Taqi Usmani",                "Islam"),
    ("Quran English Yusuf Ali",                      "Islam"),
    ("Quran English Pickthall",                      "Islam"),
    ("Quran English Sahih International",            "Islam"),
    ("Quran English Arberry",                        "Islam"),
    ("Quran Persian Farsi",                          "Islam"),
    ("Quran Turkish translation",                    "Islam"),
    ("Quran Bengali translation",                    "Islam"),
    ("Quran Tamil translation",                      "Islam"),
    ("Quran Telugu translation",                     "Islam"),
    ("Quran Gujarati translation",                   "Islam"),
    ("Quran Indonesian translation",                 "Islam"),
    ("Quran French translation",                     "Islam"),
    ("Quran German translation",                     "Islam"),
    ("Quran Spanish translation",                    "Islam"),
    ("Quran Chinese translation",                    "Islam"),
    ("Tafsir Ibn Kathir English vol 1",              "Islam"),
    ("Tafsir Ibn Kathir English vol 2",              "Islam"),
    ("Tafsir Ibn Kathir English vol 3",              "Islam"),
    ("Tafsir Ibn Kathir Urdu",                       "Islam"),
    ("Tafsir Jalalayn Arabic English",               "Islam"),
    ("Maariful Quran Urdu English",                  "Islam"),
    ("Sahih Bukhari Arabic English vol 1",           "Islam"),
    ("Sahih Bukhari Arabic English vol 2",           "Islam"),
    ("Sahih Bukhari Arabic English vol 3",           "Islam"),
    ("Sahih Bukhari Arabic English vol 4",           "Islam"),
    ("Sahih Bukhari Arabic English vol 5",           "Islam"),
    ("Sahih Bukhari Arabic English vol 6",           "Islam"),
    ("Sahih Bukhari Arabic English vol 7",           "Islam"),
    ("Sahih Bukhari Arabic English vol 8",           "Islam"),
    ("Sahih Bukhari Hindi translation",              "Islam"),
    ("Sahih Bukhari Urdu translation",               "Islam"),
    ("Sahih Muslim English vol 1",                   "Islam"),
    ("Sahih Muslim English vol 2",                   "Islam"),
    ("Sahih Muslim English vol 3",                   "Islam"),
    ("Sahih Muslim English vol 4",                   "Islam"),
    ("Sahih Muslim Urdu translation",                "Islam"),
    ("Sunan Abu Dawud English vol 1",                "Islam"),
    ("Sunan Abu Dawud English vol 2",                "Islam"),
    ("Sunan Abu Dawud Urdu translation",             "Islam"),
    ("Jami Tirmidhi English vol 1",                  "Islam"),
    ("Jami Tirmidhi English vol 2",                  "Islam"),
    ("Jami Tirmidhi English vol 3",                  "Islam"),
    ("Sunan Ibn Majah English vol 1",                "Islam"),
    ("Sunan Ibn Majah English vol 2",                "Islam"),
    ("Sunan Nasai English vol 1",                    "Islam"),
    ("Sunan Nasai English vol 2",                    "Islam"),
    ("Muwatta Imam Malik English",                   "Islam"),
    ("Sirah Ibn Hisham English",                     "Islam"),
    ("Sirah Ibn Hisham Urdu",                        "Islam"),
    ("Ihya Ulum al-Din Ghazali English vol 1",       "Islam"),
    ("Ihya Ulum al-Din Ghazali English vol 2",       "Islam"),
    ("Ihya Ulum al-Din Ghazali Urdu",                "Islam"),
    ("Rumi Masnavi Persian original",                "Islam"),
    ("Rumi Masnavi English vol 1",                   "Islam"),
    ("Rumi Masnavi English vol 2",                   "Islam"),
    ("Rumi Masnavi Hindi Urdu",                      "Islam"),
    ("Ibn Khaldun Muqaddimah English",               "Islam"),

    # ── CHRISTIANITY ──
    ("Bible King James Version",                     "Christianity"),
    ("Bible New International Version",              "Christianity"),
    ("Bible Douay Rheims Catholic",                  "Christianity"),
    ("Bible Hindi translation",                      "Christianity"),
    ("Bible Urdu translation",                       "Christianity"),
    ("Bible Tamil translation",                      "Christianity"),
    ("Bible Telugu translation",                     "Christianity"),
    ("Bible Bengali translation",                    "Christianity"),
    ("Bible Gujarati translation",                   "Christianity"),
    ("Bible Marathi translation",                    "Christianity"),
    ("Bible Kannada translation",                    "Christianity"),
    ("Bible Malayalam translation",                  "Christianity"),
    ("Bible Spanish Reina Valera",                   "Christianity"),
    ("Bible French Louis Segond",                    "Christianity"),
    ("Bible German Luther",                          "Christianity"),
    ("Bible Russian Synodal",                        "Christianity"),
    ("Bible Arabic translation",                     "Christianity"),
    ("Bible Greek Septuagint",                       "Christianity"),
    ("Bible Latin Vulgate",                          "Christianity"),
    ("Bible Chinese Union Version",                  "Christianity"),
    ("Bible Japanese translation",                   "Christianity"),
    ("Apocrypha complete English",                   "Christianity"),
    ("Dead Sea Scrolls English",                     "Christianity"),
    ("Book of Enoch English",                        "Christianity"),
    ("Book of Jubilees English",                     "Christianity"),
    ("Gospel of Thomas English",                     "Christianity"),
    ("Nag Hammadi library English",                  "Christianity"),
    ("City of God Augustine English",                "Christianity"),
    ("Confessions Augustine English",                "Christianity"),
    ("Summa Theologica Aquinas English vol 1",       "Christianity"),
    ("Summa Theologica Aquinas English vol 2",       "Christianity"),
    ("Summa Theologica Aquinas English vol 3",       "Christianity"),
    ("Imitation of Christ Kempis English",           "Christianity"),
    ("Philokalia vol 1 English",                     "Christianity"),
    ("Philokalia vol 2 English",                     "Christianity"),
    ("Early Church Fathers English",                 "Christianity"),

    # ── BUDDHISM ──
    ("Dhammapada Pali English",                      "Buddhism"),
    ("Dhammapada Hindi translation",                 "Buddhism"),
    ("Dhammapada Tamil translation",                 "Buddhism"),
    ("Dhammapada Sinhala translation",               "Buddhism"),
    ("Digha Nikaya Pali English",                    "Buddhism"),
    ("Majjhima Nikaya Pali English",                 "Buddhism"),
    ("Samyutta Nikaya Pali English",                 "Buddhism"),
    ("Anguttara Nikaya Pali English",                "Buddhism"),
    ("Khuddaka Nikaya English vol 1",                "Buddhism"),
    ("Vinaya Pitaka Pali English",                   "Buddhism"),
    ("Abhidhamma Pitaka English",                    "Buddhism"),
    ("Tripitaka Hindi translation",                  "Buddhism"),
    ("Heart Sutra Sanskrit English",                 "Buddhism"),
    ("Diamond Sutra Sanskrit English",               "Buddhism"),
    ("Lotus Sutra English",                          "Buddhism"),
    ("Lankavatara Sutra English",                    "Buddhism"),
    ("Tibetan Book of Dead English Fremantle",       "Buddhism"),
    ("Tibetan Book of Dead English Evans-Wentz",     "Buddhism"),
    ("Milarepa hundred thousand songs English",      "Buddhism"),
    ("Bodhicharyavatara Shantideva English",         "Buddhism"),
    ("Platform Sutra Huineng English",               "Buddhism"),
    ("Blue Cliff Record English",                    "Buddhism"),
    ("Shobogenzo Dogen English vol 1",               "Buddhism"),
    ("Shobogenzo Dogen English vol 2",               "Buddhism"),
    ("Visuddhimagga Buddhaghosa English",            "Buddhism"),
    ("Jataka tales Pali English",                    "Buddhism"),
    ("Buddhism Hindi Ambedkar",                      "Buddhism"),

    # ── SIKHISM ──
    ("Guru Granth Sahib Punjabi Gurmukhi",           "Sikhism"),
    ("Guru Granth Sahib Hindi translation",          "Sikhism"),
    ("Guru Granth Sahib English translation",        "Sikhism"),
    ("Dasam Granth Punjabi English",                 "Sikhism"),
    ("Japji Sahib Punjabi Hindi English",            "Sikhism"),
    ("Sukhmani Sahib Punjabi Hindi English",         "Sikhism"),
    ("Bhai Gurdas Vaaran Punjabi English",           "Sikhism"),
    ("Guru Nanak biography English",                 "Sikhism"),

    # ── JUDAISM ──
    ("Torah Hebrew English complete",                "Judaism"),
    ("Babylonian Talmud English Soncino vol 1",      "Judaism"),
    ("Babylonian Talmud English Soncino vol 2",      "Judaism"),
    ("Babylonian Talmud English Soncino vol 3",      "Judaism"),
    ("Babylonian Talmud English Soncino vol 4",      "Judaism"),
    ("Babylonian Talmud English Soncino vol 5",      "Judaism"),
    ("Babylonian Talmud Hebrew Aramaic",             "Judaism"),
    ("Jerusalem Talmud English",                     "Judaism"),
    ("Mishnah Hebrew English",                       "Judaism"),
    ("Zohar English Sperling vol 1",                 "Judaism"),
    ("Zohar English Sperling vol 2",                 "Judaism"),
    ("Zohar English Sperling vol 3",                 "Judaism"),
    ("Midrash Rabbah English vol 1",                 "Judaism"),
    ("Midrash Rabbah English vol 2",                 "Judaism"),
    ("Maimonides Guide Perplexed English",           "Judaism"),
    ("Pirkei Avot Hebrew English",                   "Judaism"),
    ("Tanya Lubavitch English",                      "Judaism"),

    # ── ZOROASTRIANISM ──
    ("Avesta English Darmesteter",                   "Zoroastrianism"),
    ("Gathas Zarathustra English",                   "Zoroastrianism"),
    ("Yasna Avesta English",                         "Zoroastrianism"),
    ("Vendidad Avesta English",                      "Zoroastrianism"),
    ("Bundahishn English translation",               "Zoroastrianism"),
    ("Denkard Middle Persian English",               "Zoroastrianism"),
    ("Pahlavi texts Sacred Books East",              "Zoroastrianism"),

    # ── JAINISM ──
    ("Tattvartha Sutra Hindi English",               "Jainism"),
    ("Acaranga Sutra English",                       "Jainism"),
    ("Uttaradhyayana Sutra English",                 "Jainism"),
    ("Kalpa Sutra English Jacobi",                   "Jainism"),
    ("Jain Agamas English complete",                 "Jainism"),
    ("Samayasara Kundakunda English",                "Jainism"),
    ("Jain sacred texts Sacred Books East",          "Jainism"),

    # ── TAOISM & CONFUCIANISM ──
    ("Tao Te Ching Chinese original",               "Taoism_Confucianism"),
    ("Tao Te Ching English Legge",                  "Taoism_Confucianism"),
    ("Tao Te Ching Hindi translation",              "Taoism_Confucianism"),
    ("Zhuangzi Chinese English",                    "Taoism_Confucianism"),
    ("I Ching English Wilhelm",                     "Taoism_Confucianism"),
    ("Analects Confucius English Legge",            "Taoism_Confucianism"),
    ("Mencius English Legge",                       "Taoism_Confucianism"),
    ("Five Classics Confucian English",             "Taoism_Confucianism"),

    # ── SHINTO ──
    ("Kojiki Japanese English Chamberlain",         "Shinto"),
    ("Nihon Shoki English translation",             "Shinto"),
    ("Norito Shinto prayers English",               "Shinto"),

    # ── BAHAI ──
    ("Kitab i Aqdas Bahaullah English",              "Bahai"),
    ("Kitab i Iqan Bahaullah English",               "Bahai"),
    ("Hidden Words Bahaullah English",               "Bahai"),
    ("Seven Valleys Bahaullah English",              "Bahai"),
    ("Some Answered Questions Abdulbaha",            "Bahai"),
    ("Dawn-Breakers Nabil English",                  "Bahai"),

    # ── NORSE ──
    ("Prose Edda Snorri English",                    "Norse_Germanic"),
    ("Poetic Edda English Bellows",                  "Norse_Germanic"),
    ("Havamal Old Norse English",                    "Norse_Germanic"),
    ("Volsunga Saga English",                        "Norse_Germanic"),
    ("Icelandic Sagas English",                      "Norse_Germanic"),

    # ── GREEK & ROMAN ──
    ("Theogony Hesiod Greek English",                "Greek_Roman"),
    ("Iliad Homer English",                          "Greek_Roman"),
    ("Odyssey Homer English",                        "Greek_Roman"),
    ("Homeric Hymns Greek English",                  "Greek_Roman"),
    ("Plato Dialogues English complete",             "Greek_Roman"),
    ("Orphic Hymns Greek English",                   "Greek_Roman"),

    # ── EGYPTIAN ──
    ("Egyptian Book of Dead English Budge",          "Egyptian"),
    ("Egyptian Book of Dead English Faulkner",       "Egyptian"),
    ("Pyramid Texts English Faulkner",               "Egyptian"),
    ("Coffin Texts English Faulkner",                "Egyptian"),

    # ── MESOPOTAMIAN ──
    ("Epic of Gilgamesh English Andrew George",      "Mesopotamian"),
    ("Enuma Elish English translation",              "Mesopotamian"),
    ("Sumerian mythology Kramer English",            "Mesopotamian"),

    # ── MESOAMERICAN ──
    ("Popol Vuh Mayan English Tedlock",              "Mesoamerican"),
    ("Chilam Balam English",                         "Mesoamerican"),
    ("Florentine Codex Sahagun English vol 1",       "Mesoamerican"),

    # ── GNOSTICISM ──
    ("Nag Hammadi scriptures English",               "Gnosticism"),
    ("Pistis Sophia English",                        "Gnosticism"),
    ("Corpus Hermetica Greek English",               "Gnosticism"),
    ("Kybalion Hermetic English",                    "Gnosticism"),

    # ── AFRICAN ──
    ("Ifa corpus Yoruba English",                    "African"),
    ("African religions Mbiti English",              "African"),

    # ── INDIGENOUS ──
    ("Black Elk Speaks English",                     "Indigenous"),
    ("The Sacred Pipe English",                      "Indigenous"),
    ("Native American religions English",            "Indigenous"),

    # ── RASTAFARIANISM ──
    ("Holy Piby Rastafari English",                  "Rastafarianism"),
    ("Kebra Nagast English Budge",                   "Rastafarianism"),
    ("Ethiopian Orthodox Bible English",             "Rastafarianism"),

    # ── THEOSOPHY ──
    ("Secret Doctrine Blavatsky vol 1",              "Theosophy"),
    ("Secret Doctrine Blavatsky vol 2",              "Theosophy"),
    ("Isis Unveiled Blavatsky vol 1",                "Theosophy"),
    ("Key to Theosophy Blavatsky",                   "Theosophy"),
    ("Steiner How to Know Higher Worlds",            "Theosophy"),

    # ── WICCA ──
    ("Book of Shadows Gardner Wicca",                "Wicca"),
    ("Mabinogion Welsh mythology English",           "Wicca"),
    ("Celtic Druids texts English",                  "Wicca"),

    # ── MANDAEISM & YAZIDISM ──
    ("Ginza Rba Mandaean English",                   "Mandaeism"),
    ("Kitab al-Jilwa Yazidi English",                "Yazidism"),

    # ── TENRIKYO ──
    ("Ofudesaki Tenrikyo Japanese English",          "Tenrikyo"),
    ("Mikagura Uta Tenrikyo English",                "Tenrikyo"),

    # ── COMPARATIVE RELIGION ──
    ("Sacred Books East Muller vol 1",               "Comparative"),
    ("Sacred Books East Muller vol 2",               "Comparative"),
    ("Sacred Books East Muller vol 3",               "Comparative"),
    ("Sacred Books East Muller vol 4",               "Comparative"),
    ("Sacred Books East Muller vol 5",               "Comparative"),
    ("Sacred Books East Muller vol 6",               "Comparative"),
    ("Sacred Books East Muller vol 7",               "Comparative"),
    ("Sacred Books East Muller vol 8",               "Comparative"),
    ("Sacred Books East Muller vol 9",               "Comparative"),
    ("Sacred Books East Muller vol 10",              "Comparative"),
    ("Perennial Philosophy Huxley",                  "Comparative"),
    ("World religions Huston Smith",                 "Comparative"),
    ("Golden Bough Frazer vol 1",                    "Comparative"),
    ("Golden Bough Frazer vol 2",                    "Comparative"),
    ("Hero thousand faces Joseph Campbell",          "Comparative"),
    ("Masks of God Campbell vol 1",                  "Comparative"),
    ("Masks of God Campbell vol 2",                  "Comparative"),
    ("Masks of God Campbell vol 3",                  "Comparative"),
    ("Masks of God Campbell vol 4",                  "Comparative"),
    ("History of God Karen Armstrong",               "Comparative"),
    ("Varieties Religious Experience James",         "Comparative"),
]


# ─────────────────────────────────────────────────────────────
#  TRACKER
# ─────────────────────────────────────────────────────────────

def get_downloaded():
    if not os.path.exists(TRACKER_FILE):
        return set()
    with open(TRACKER_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def mark_downloaded(key):
    with lock:
        with open(TRACKER_FILE, "a") as f:
            f.write(key + "\n")

def mark_failed(query, religion):
    with lock:
        with open(FAILED_FILE, "a") as f:
            f.write(f"{query} | {religion}\n")


# ─────────────────────────────────────────────────────────────
#  ARCHIVE.ORG SEARCH + DOWNLOAD
# ─────────────────────────────────────────────────────────────

def search_archive(query):
    try:
        r = requests.get(
            "https://archive.org/advancedsearch.php",
            params={
                "q": f'({query}) AND mediatype:texts',
                "fl[]": ["identifier", "title"],
                "rows": 3,
                "page": 1,
                "output": "json",
                "sort[]": "downloads desc"
            },
            timeout=15
        )
        docs = r.json().get("response", {}).get("docs", [])
        return [{"identifier": d.get("identifier",""), "title": d.get("title","")} for d in docs if d.get("identifier")]
    except:
        return []

def get_pdf_url(identifier):
    try:
        r = requests.get(f"https://archive.org/metadata/{identifier}", timeout=15)
        for f in r.json().get("files", []):
            if f.get("name","").lower().endswith(".pdf"):
                return f"https://archive.org/download/{identifier}/{f['name']}", f["name"]
    except:
        pass
    return None, None

def download_file(url, save_path):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    r = requests.get(url, headers=headers, timeout=60, stream=True)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    return False


# ─────────────────────────────────────────────────────────────
#  WORKER — runs for each query in parallel
# ─────────────────────────────────────────────────────────────

def process_query(args):
    idx, total, query, religion, already_done = args

    pct  = int(((idx + 1) / total) * 100)
    prog = f"[{idx+1}/{total} | {pct}%]"

    # Skip if already downloaded
    if query in already_done:
        with lock:
            skipped_count[0] += 1
        print(f"{prog} SKIP  {query}")
        return

    religion_folder = os.path.join(SAVE_FOLDER, religion)
    os.makedirs(religion_folder, exist_ok=True)

    print(f"{prog} SEARCH: {query}")

    results = search_archive(query)
    if not results:
        with lock:
            failed_count[0] += 1
        mark_failed(query, religion)
        print(f"{prog} NO RESULTS: {query}")
        return

    for result in results:
        identifier = result["identifier"]
        title      = result["title"][:50]
        pdf_url, _ = get_pdf_url(identifier)

        if not pdf_url:
            continue

        safe_name = query[:55].replace(" ", "_").replace("/","_") + ".pdf"
        save_path = os.path.join(religion_folder, safe_name)

        try:
            if download_file(pdf_url, save_path):
                size_kb = os.path.getsize(save_path) / 1024
                mark_downloaded(query)
                with lock:
                    downloaded_count[0] += 1
                print(f"{prog} SAVED: {safe_name} ({size_kb:.0f} KB)")
                return
        except Exception as e:
            pass

    with lock:
        failed_count[0] += 1
    mark_failed(query, religion)
    print(f"{prog} FAILED: {query}")


# ─────────────────────────────────────────────────────────────
#  MAIN — parallel execution
# ─────────────────────────────────────────────────────────────

def main():
    already_done = get_downloaded()
    total        = len(SEARCH_QUERIES)

    print("=" * 64)
    print("   PRAMAN.AI — FAST Holy Books Downloader")
    print(f"   Total Queries    : {total}")
    print(f"   Parallel Workers : {WORKERS}  (downloading {WORKERS} at once)")
    print(f"   Speed vs old     : ~{WORKERS}x faster")
    print(f"   Already Done     : {len(already_done)}")
    print(f"   Remaining        : {total - len(already_done)}")
    print("=" * 64)
    print(f"  Downloading {WORKERS} books simultaneously...")
    print("=" * 64)

    start_time = time.time()

    # Build task list
    tasks = [
        (i, total, query, religion, already_done)
        for i, (query, religion) in enumerate(SEARCH_QUERIES)
    ]

    # Run all tasks with thread pool — WORKERS at a time
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(process_query, task) for task in tasks]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                pass

    elapsed = time.time() - start_time
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)

    print("\n" + "=" * 64)
    print("   DOWNLOAD COMPLETE")
    print("=" * 64)
    print(f"   Downloaded  : {downloaded_count[0]}")
    print(f"   Skipped     : {skipped_count[0]}")
    print(f"   Failed      : {failed_count[0]}")
    print(f"   Total time  : {mins}m {secs}s")
    print(f"   Location    : {SAVE_FOLDER}/")
    if failed_count[0] > 0:
        print(f"   Failed list : {FAILED_FILE}")
        print(f"   Run again to auto-retry failed ones")
    print("=" * 64)
    print()
    print("  NEXT: Drag holy_books_pdfs folder into Praman Admin Panel")
    print("=" * 64)

if __name__ == "__main__":
    main()