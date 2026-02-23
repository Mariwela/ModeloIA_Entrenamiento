import aiohttp
import asyncio

async def send_report_to_external_mcp(report: str):
    """
    Envía el informe a un webhook de Zapier.
    """
    zapier_webhook_url = "https://hooks.zapier.com/hooks/catch/26563132/ucxatgv/"  # zapier web hook

    async with aiohttp.ClientSession() as session:
        async with session.post(zapier_webhook_url, json={"content": report}) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                print(f"⚠️ Error enviando a Zapier: {resp.status}")
                return {"error": resp.status}