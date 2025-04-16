import os
import kopf
import base64
import aiohttp
import aio_pika
import kubernetes


@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'shovels')
async def create_shovel(spec, namespace, logger, **kwargs):
    shovel_name = kwargs['meta']['name']
    vhost = "%2F"
    reconnect_delay = spec.get("reconnectDelay", 5)

    source_uri = spec["sourceURI"]
    destination_uri = spec["destinationURI"]

    src = {}
    dst = {}

    if "sourceQueue" in spec:
        src["src-queue"] = spec["sourceQueue"]
    elif "sourceExchange" in spec:
        src["src-exchange"] = spec["sourceExchange"]
        if "routingKey" in spec:
            src["src-exchange-key"] = spec["routingKey"]

    if "destinationQueue" in spec:
        dst["dest-queue"] = spec["destinationQueue"]
    elif "destinationExchange" in spec:
        dst["dest-exchange"] = spec["destinationExchange"]

    secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-operator-con")
    secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")
    k8s = kubernetes.client.CoreV1Api()
    secret = k8s.read_namespaced_secret(secret_name, namespace)
    rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

    from urllib.parse import urlparse
    parsed = urlparse(rabbit_url)
    http_api_url = f"http://{parsed.hostname}:15672/api/parameters/shovel/{vhost}/{shovel_name}"
    auth = aiohttp.BasicAuth(parsed.username, parsed.password)

    payload = {
        "value": {
            **src,
            **dst,
            "src-uri": source_uri,
            "dest-uri": destination_uri,
            "ack-mode": "on-confirm",
            "delete-after": "never",
            "reconnect-delay": reconnect_delay
        }
    }

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.put(http_api_url, json=payload) as resp:
            if resp.status != 201:
                error = await resp.text()
                raise kopf.PermanentError(f"Failed to create shovel: {resp.status} - {error}")

    logger.info(f"Shovel '{shovel_name}' criado com sucesso.")
    return {"shovel": shovel_name, "status": "created"}

@kopf.on.delete('rabbitmq.bruno.io', 'v1alpha1', 'shovels')
async def delete_shovel(spec, name, namespace, logger, **kwargs):
    try:
        # Buscar RabbitMQ URI da Secret
        secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-operator-con")
        secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")

        k8s = kubernetes.client.CoreV1Api()
        secret = k8s.read_namespaced_secret(secret_name, namespace)
        rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

        from urllib.parse import urlparse, quote
        parsed = urlparse(rabbit_url)
        vhost = quote("/", safe="")  # codifica "/"
        http_api_url = f"http://{parsed.hostname}:15672/api/parameters/shovel/{vhost}/{name}"
        auth = aiohttp.BasicAuth(parsed.username, parsed.password)

        # Deletar o shovel via HTTP API
        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.delete(http_api_url) as resp:
                if resp.status not in [204, 200]:
                    error = await resp.text()
                    raise kopf.PermanentError(f"Erro ao deletar shovel: {resp.status} - {error}")

        logger.info(f"Shovel '{name}' removido com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao remover shovel '{name}': {e}")
        raise kopf.TemporaryError(f"Erro ao remover shovel '{name}'", delay=30)
