import asyncio
import json
import pytz
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser
import aiofiles

API_KEY = os.getenv("TAIMOUR_API_KEY")

def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

PKT = pytz.timezone("Asia/Karachi")

class Article(BaseModel):
    title: str
    url: str
    summary: str
    section: str
    date: str
    imageUrl: Optional[str] = None


class DayArchive(BaseModel):
    date: str
    sections: Dict[str, List[Article]]
    cached_at: Optional[str] = None


class DawnScraper:
    def __init__(self):
        self.base_url = "https://www.dawn.com/newspaper"
        self.data_dir = Path("./data")
        self.delay = 2
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.cache: Dict[str, DayArchive] = {}

    async def init_browser(self):
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
        return self.browser

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    def resolve_image_url(self, article_soup) -> Optional[str]:
        img = article_soup.find('img')
        picture = article_soup.find('picture')

        if img:
            for attr in ['data-src', 'data-original']:
                url = img.get(attr)
                if url and not url.startswith('data:image'):
                    return url

            srcset = img.get('srcset')
            if srcset:
                first = srcset.split(',')[0].strip().split(' ')[0]
                if not first.startswith('data:image'):
                    return first

        if picture:
            source = picture.find('source')
            if source:
                srcset = source.get('srcset')
                if srcset:
                    first = srcset.split(',')[0].strip().split(' ')[0]
                    return first

        if img:
            url = img.get('src')
            if url and not url.startswith('data:image'):
                return url

        return None

    async def fetch_page(self, url: str) -> str:
        browser = await self.init_browser()
        page = await browser.new_page()

        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        print(f"  Fetching: {url}")
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"  Timeout or navigation error for {url}, Error {e}, retrying...")
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as err2:
                print(f"  Failed again: {err2}")
                await page.close()
                raise err2

        html = await page.content()
        await page.close()
        return html

    def parse_section(self, html: str, section: str, date: str) -> List[Article]:
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        selectors = [
            'article.story',
            '.story',
            'article',
            '.box.story',
            '.story-list article'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if not elements:
                continue

            for el in elements:
                title_el = el.select_one('h2 a, .story__title a, h3 a, .story__link')
                summary_el = el.select_one('.story__excerpt, .story__text, p')

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                url = title_el.get('href')
                summary = summary_el.get_text(strip=True) if summary_el else ''

                if not title or not url:
                    continue

                # Skip duplicates
                if any(a.title == title for a in articles):
                    continue

                raw_image = self.resolve_image_url(el)
                image_url = None

                if raw_image:
                    if raw_image.startswith('//'):
                        image_url = f"https:{raw_image}"
                    elif raw_image.startswith('http'):
                        image_url = raw_image
                    else:
                        image_url = f"https://www.dawn.com{raw_image}"

                article_url = url if url.startswith('http') else f"https://www.dawn.com{url}"

                article = Article(
                    title=title,
                    url=article_url,
                    summary=summary,
                    section=section,
                    date=date,
                    imageUrl=image_url
                )
                articles.append(article)

            if articles:
                break

        return articles

    async def scrape_day(self, date_string: str) -> DayArchive:
        sections = ['front-page', 'back-page', 'national', 'editorial', 'business']
        day_archive = DayArchive(
            date=date_string,
            sections={},
            cached_at=datetime.now().isoformat()
        )

        await self.init_browser()

        for section in sections:
            print(f"Scraping {section} for {date_string}...")
            try:
                url = f"{self.base_url}/{section}/{date_string}"
                html = await self.fetch_page(url)
                articles = self.parse_section(html, section, date_string)

                day_archive.sections[section] = articles
                print(f"  Found {len(articles)} articles")

                await asyncio.sleep(self.delay)
            except Exception as err:
                print(f"Failed to scrape {section} for {date_string}: {err}")
                day_archive.sections[section] = []

        await self.close_browser()

        # Save to file
        await self.save_archive(day_archive)

        # Cache it
        self.cache[date_string] = day_archive

        return day_archive

    async def save_archive(self, day_archive: DayArchive):
        self.data_dir.mkdir(exist_ok=True)
        file_path = self.data_dir / f"{day_archive.date}.json"

        async with aiofiles.open(file_path, 'w') as f:
            await f.write(day_archive.model_dump_json(indent=2))

        print(f"Archive saved to {file_path}")

    async def load_archive(self, date_string: str) -> Optional[DayArchive]:
        file_path = self.data_dir / f"{date_string}.json"
        if not file_path.exists():
            return None

        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                data = DayArchive.model_validate_json(content)
                self.cache[date_string] = data
                return data
        except Exception as e:
            print(f"Error loading archive for {date_string}: {e}")
            return None

    def get_todays_date(self) -> str:
        now = datetime.now(PKT)
        past = now.replace(year=now.year - 12)
        return past.strftime('%Y-%m-%d')

    def get_tomorrows_date(self) -> str:
        tomorrow = datetime.now(PKT) + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')        

    def get_tomorrows_date(self) -> str:
        today_str = self.get_todays_date()
        today_dt = datetime.strptime(today_str, '%Y-%m-%d')
        tomorrow_dt = today_dt + timedelta(days=1)        
        return tomorrow_dt.strftime('%Y-%m-%d')        

    async def ensure_tomorrow_exists(self):
        """Scrape tomorrow's data if it doesn't exist"""
        tomorrow = self.get_tomorrows_date()
        file_path = self.data_dir / f"{tomorrow}.json"
        
        if file_path.exists():
            print(f"Tomorrow's data already exists: {tomorrow}")
            return
        
        print(f"Precomputing tomorrow's data: {tomorrow}")
        try:
            await self.scrape_day(tomorrow)
        except Exception as e:
            print(f"Error precomputing tomorrow: {e}")


# Global scraper instance
scraper = DawnScraper()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown: cleanup
    await scraper.close_browser()


app = FastAPI(
    title="Dawn Archive API",
    description="API for scraping Dawn newspaper archives",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", dependencies=[Depends(validate_api_key)])
async def root():
    return {
        "message": "Dawn Archive API",
        "endpoints": {
            "/api/today": "Get today's articles (always cached)",
            "/api/date/{date}": "Get specific date (YYYY-MM-DD)",
            "/api/cache": "View cached dates"
        }
    }


@app.get("/api/today", dependencies=[Depends(validate_api_key)])
async def get_today(background_tasks: BackgroundTasks):
    """
    Get today's articles. Always returns cached data.
    After returning, precomputes tomorrow's data in background.
    """
    today = scraper.get_todays_date()

    
    # Remove old files before today
    data_dir = Path(scraper.data_dir)
    for file in data_dir.glob("*.json"):
        # Assume filename is YYYY-MM-DD.json
        try:
            file_date = file.stem
            if file_date < today:
                file.unlink()
        except Exception as e:
            print(f"Error deleting file {file}: {e}")    
    
    # Load from file (should always exist)
    archive = await scraper.load_archive(today)
    
    if not archive:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for today ({today}). Please ensure data files exist."
        )
    
    # In background, ensure tomorrow exists
    background_tasks.add_task(scraper.ensure_tomorrow_exists)
    
    return archive


@app.get("/api/date/{date}", dependencies=[Depends(validate_api_key)])
async def get_date(date: str, background_tasks: BackgroundTasks):
    """
    Get articles for a specific date (YYYY-MM-DD).
    If cached, returns immediately. Otherwise scrapes.
    After returning, precomputes next day in background.
    """
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Try loading from file first
    archive = await scraper.load_archive(date)
    
    if not archive:
        # Scrape if not available
        print(f"Data not found for {date}, scraping...")
        try:
            archive = await scraper.scrape_day(date)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error scraping: {str(e)}")
    
    # In background, ensure next day exists
    async def precompute_next_day():
        try:
            requested_date = datetime.strptime(date, '%Y-%m-%d')
            next_day = (requested_date + timedelta(days=1)).strftime('%Y-%m-%d')
            file_path = scraper.data_dir / f"{next_day}.json"
            
            if not file_path.exists():
                print(f"Precomputing next day: {next_day}")
                await scraper.scrape_day(next_day)
        except Exception as e:
            print(f"Error precomputing next day: {e}")
    
    background_tasks.add_task(precompute_next_day)
    
    return archive


@app.get("/api/cache", dependencies=[Depends(validate_api_key)])
async def get_cache_info():
    """Get information about cached dates in memory"""
    return {
        "cached_dates": list(scraper.cache.keys()),
        "count": len(scraper.cache)
    }


@app.get("/api/files", dependencies=[Depends(validate_api_key)])
async def get_files_info():
    """Get information about available data files on disk"""
    data_dir = Path("./data")
    if not data_dir.exists():
        return {"files": [], "count": 0}
    
    files = sorted([f.stem for f in data_dir.glob("*.json")])
    return {
        "files": files,
        "count": len(files)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)