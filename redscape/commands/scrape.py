import click
import asyncio
from redscape.core.scraper import PlaywrightScraper

@click.command()
@click.argument('url')
@click.option('--depth', '-d', default=1, help='Crawl depth')
@click.option('--screenshot', '-s', is_flag=True, help='Capture screenshots')
@click.pass_context
def scrape(ctx, url, depth, screenshot):
    """Scrape target URL"""
    click.echo(f"[+] Target: {url}")
    click.echo(f"[+] Depth: {depth}")
    click.echo(f"[+] Screenshots: {'enabled' if screenshot else 'disabled'}")
    click.echo("[+] Initializing scraper...")
    
    scraper = PlaywrightScraper()
    
    try:
        results = asyncio.run(scraper.crawl(url, depth=depth, screenshot=screenshot))
        
        click.echo(f"\n[+] Case ID: {results['case_id']}")
        click.echo(f"[+] Pages scraped: {len(results['pages'])}")
        
        for page in results['pages']:
            status = "✓" if 'error' not in page else "✗"
            click.echo(f"  [{status}] {page['url']}")
            if 'error' in page:
                click.echo(f"      Error: {page['error']}")
        
        if screenshot:
            click.echo(f"\n[+] Screenshots saved to: {results['evidence_dir']}")
            
    except Exception as e:
        click.echo(f"[-] Fatal error: {e}", err=True)