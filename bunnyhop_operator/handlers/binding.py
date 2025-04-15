import kopf
import aio_pika
import os
import base64
import kubernetes

@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'bindings')
async def create_binding(spec, namespace, logger, **kwargs):
    exchange_name = spec['exchange']
    queue_name = spec['queue']
    routing_key = spec['routingKey']

    secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-rabbitmq-connection")
    secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")
    k8s = kubernetes.client.CoreV1Api()
    secret = k8s.read_namespaced_secret(secret_name, namespace)
    rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

    connection = await aio_pika.connect_robust(rabbit_url)
    channel = await connection.channel()

    exchange = await channel.get_exchange(exchange_name)
    queue = await channel.get_queue(queue_name)

    await queue.bind(exchange, routing_key=routing_key)

    await connection.close()
    logger.info(f"Bound queue '{queue_name}' to exchange '{exchange_name}' with key '{routing_key}'.")
    return {"binding": f"{exchange_name} -> {queue_name}", "status": "bound"}
    
@kopf.on.delete('rabbitmq.bruno.io', 'v1alpha1', 'bindings')
async def delete_binding(spec, name, namespace, logger, **kwargs):
    exchange = spec["exchange"]
    queue = spec["queue"]
    routing_key = spec["routingKey"]

    try:
        secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-rabbitmq-connection")
        secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")
        k8s = kubernetes.client.CoreV1Api()
        secret = k8s.read_namespaced_secret(secret_name, namespace)
        rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

        connection = await aio_pika.connect_robust(rabbit_url)
        channel = await connection.channel()

        exchange_obj = await channel.get_exchange(exchange)
        queue_obj = await channel.get_queue(queue)

        await queue_obj.unbind(exchange_obj, routing_key=routing_key)
        await connection.close()

        logger.info(f"Binding '{queue}' ← '{exchange}' com routing key '{routing_key}' removido.")
    except Exception as e:
        logger.error(f"Erro ao remover binding '{queue}' de '{exchange}': {e}")
        raise kopf.TemporaryError(f"Erro ao remover binding '{queue}' de '{exchange}'", delay=30)
