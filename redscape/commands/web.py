import click  
from redscape.interface.web import start_interface  
  
@click.command()  
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind')  
@click.option('--port', '-p', default=5000, help='Port to bind')  
@click.option('--debug', '-d', is_flag=True, help='Debug mode')  
def web(host, port, debug):  
    """Start Redscape Archive interface"""  
    click.echo(f"[+] Starting Redscape Archive")  
    click.echo(f"[+] Host: {host}:{port}")  
    start_interface(host=host, port=port, debug=debug)  