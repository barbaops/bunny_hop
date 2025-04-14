import kopf
import aio_pika
import os
import base64
import kubernetes

@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'exchanges')
async def create_exchange(spec, namespace, logger, **kwargs):
    exchange_name = spec['name']
    exchange_type = spec['type']
    durable = spec.get('durable', True)
    auto_delete = spec.get('autoDelete', False)

    secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-rabbitmq-connection")
    secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")
    k8s = kubernetes.client.CoreV1Api()
    secret = k8s.read_namespaced_secret(secret_name, namespace)
    rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

    connection = await aio_pika.connect_robust(rabbit_url)
    channel = await connection.channel()
    await channel.declare_exchange(
        name=exchange_name,
        type=exchange_type,
        durable=durable,
        auto_delete=auto_delete,
    )
    await connection.close()
    logger.info(f"Exchange '{exchange_name}' created.")
    return {"exchange": exchange_name, "status": "created"}
