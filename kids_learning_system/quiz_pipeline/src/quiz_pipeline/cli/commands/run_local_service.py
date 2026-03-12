import uvicorn
import typer
from quiz_pipeline.local_service.config import settings

app = typer.Typer()

@app.command()
def main(lan: bool = typer.Option(False, "--lan", help="Enable LAN mode (accessible from other devices on the network)")):
    """Run the local FastAPI quiz service."""
    settings.LAN_MODE = lan
    settings.apply_lan_mode()
    host = settings.SERVER_HOST
    port = settings.SERVER_PORT
    mode = "LAN MODE" if lan else "LOCAL MODE"
    print(f"\n=== Quiz Platform {mode} ===")
    print(f"Server running at: http://{host}:{port}")
    if lan:
        lan_ip = settings.get_lan_ip()
        print(f"LAN Access:   http://{lan_ip}:{port}")
        print("\nSECURITY: This server is for LAN use only. Do NOT expose it to the internet via port forwarding!\n")
    uvicorn.run(
        "quiz_pipeline.local_service.app:app",
        host=host,
        port=port,
        reload=False
    )

if __name__ == "__main__":
    app()
