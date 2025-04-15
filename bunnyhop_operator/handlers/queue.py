import os
import kopf
import base64
import aio_pika
import kubernetes

from aio_pika.exceptions import ChannelNotFoundEntity

@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'queues')
async def create_queue(spec, name, namespace, logger, **kwargs):
    queue_name = spec.get("name", name)
    durable = spec.get("durable", True)
    auto_delete = spec.get("autoDelete", False)
    arguments = spec.get("arguments", {})

    try:
        # Carregando URL do RabbitMQ via Secret do Kubernetes
        secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-operator-con")
        secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")

        k8s = kubernetes.client.CoreV1Api()
        secret = k8s.read_namespaced_secret(secret_name, namespace)
        rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

        # Conexão e criação da fila
        connection = await aio_pika.connect_robust(rabbit_url)
        channel = await connection.channel()

        await channel.declare_queue(
            name=queue_name,
            durable=durable,
            auto_delete=auto_delete,
            arguments=arguments
        )

        logger.info(f"Queue '{queue_name}' created.")
        await connection.close()

    except Exception as e:
        logger.error(f"Erro ao criar fila '{queue_name}': {e}")
        raise kopf.TemporaryError(f"Erro ao criar fila '{queue_name}'", delay=30)

@kopf.on.delete('rabbitmq.bruno.io', 'v1alpha1', 'queues')
async def delete_queue(spec, name, namespace, logger, **kwargs):
    queue_name = spec.get('name', name)

    secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-operator-con")
    secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")

    k8s_client = kubernetes.client.CoreV1Api()
    secret = k8s_client.read_namespaced_secret(secret_name, namespace)
    rabbit_url = base64.b64decode(secret.data[secret_key]).decode()

    try:
        connection = await aio_pika.connect_robust(rabbit_url)
        channel = await connection.channel()

        await channel.queue_delete(queue_name)
        logger.info(f"Queue '{queue_name}' deleted.")
        await connection.close()
    except Exception as e:
        logger.error(f"Erro ao deletar fila '{queue_name}': {e}")
        raise kopf.TemporaryError(f"Erro ao deletar fila '{queue_name}'", delay=30)
