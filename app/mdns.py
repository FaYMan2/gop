import socket
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf
from app.constants import SERVER_NAME

ZEROCONF_TYPE = "_http._tcp.local."
SERVICE_NAME = f"{SERVER_NAME}._http._tcp.local."
PORT = 8000


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


async def register_service():
    ip = get_local_ip()

    info = ServiceInfo(
        type_=ZEROCONF_TYPE,
        name=SERVICE_NAME,
        addresses=[socket.inet_aton(ip)],
        port=PORT,
        properties={
            "path": "/",
            "app": "localsync"
        },
        server=f"{SERVER_NAME}.local."
    )

    azc = AsyncZeroconf()
    await azc.async_register_service(info)

    return azc, info
