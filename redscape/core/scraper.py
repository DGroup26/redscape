import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import hashlib
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

class PlaywrightScraper:
    def __init__(self, config=None):
        self.config = config or {}
        self.headless = self.config.get('headless', True)
        self.timeout = self.config.get('timeout', 30000)
        self.data_dir = Path.home() / ".redscape" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def crawl(self, url, depth=1, screenshot=False):
        """Crawl target URL and extract content"""
        results = {
            'case_id': self._generate_case_id(url),
            'target': url,
            'timestamp': datetime.utcnow().isoformat(),
            'pages': [],
            'evidence_dir': None
        }
        
        if screenshot:
            evidence_dir = self.data_dir / "screenshots" / results['case_id']
            evidence_dir.mkdir(parents=True, exist_ok=True)
            results['evidence_dir'] = str(evidence_dir)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            
            visited = set()
            to_visit = [(url, 0)]
            
            while to_visit:
                current_url, current_depth = to_visit.pop(0)
                
                if current_url in visited or current_depth > depth:
                    continue
                    
                visited.add(current_url)
                
                try:
                    page = await context.new_page()
                    await page.goto(current_url, timeout=self.timeout)
                    await page.wait_for_load_state('networkidle')
                    
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    page_data = {
                        'url': current_url,
                        'title': await page.title(),
                        'text': soup.get_text(separator='\n', strip=True),
                        'links': [a.get('href') for a in soup.find_all('a', href=True)],
                        'depth': current_depth
                    }
                    
                    if screenshot:
                        screenshot_path = evidence_dir / f"page_{len(results['pages'])}.png"
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                        page_data['screenshot'] = str(screenshot_path)
                    
                    results['pages'].append(page_data)
                    
                    # Add new links to queue
                    if current_depth < depth:
                        for link in page_data['links']:
                            absolute = urljoin(current_url, link)
                            if self._same_domain(url, absolute):
                                to_visit.append((absolute, current_depth + 1))
                    
                    await page.close()
                    
                except Exception as e:
                    results['pages'].append({
                        'url': current_url,
                        'error': str(e),
                        'depth': current_depth
                    })
            
            await browser.close()
        
        return results
    
    def _generate_case_id(self, url):
        """Generate unique case ID from URL and timestamp"""
        data = f"{url}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _same_domain(self, url1, url2):
        """Check if two URLs share the same domain"""
        return urlparse(url1).netloc == urlparse(url2).netloc