import os
import kopf
import base64
import aio_pika
import kubernetes

from utils.rabbitmq_conn import RabbitMQConnectionFactory


@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'queues')
async def create_queue(spec, name, namespace, logger, **kwargs):
    factory = RabbitMQConnectionFactory(namespace)
    connection = await factory.get_connection()
    channel = await connection.channel()

    arguments = spec.get("arguments", {})

    if "x-message-ttl" in arguments:
        try:
            arguments["x-message-ttl"] = int(arguments["x-message-ttl"])
        except ValueError:
            raise kopf.PermanentError("O valor de x-message-ttl deve ser um número inteiro.")

    await channel.declare_queue(
        name=spec.get("name", name),
        durable=spec.get("durable", True),
        auto_delete=spec.get("autoDelete", False),
        arguments=spec.get("arguments", {})
    )

    logger.info(f"Fila '{name}' criada.")
    await connection.close()

@kopf.on.delete('rabbitmq.bruno.io', 'v1alpha1', 'queues')
async def delete_queue(spec, name, namespace, logger, **kwargs):
    factory = RabbitMQConnectionFactory(namespace)
    connection = await factory.get_connection()
    channel = await connection.channel()
    
    queue_name = spec.get("name", name)

    try:
        await channel.queue_delete(queue_name)
        logger.info(f"Queue '{queue_name}' deleted.")
        await connection.close()
    except Exception as e:
        logger.error(f"Erro ao deletar fila '{queue_name}': {e}")
        raise kopf.TemporaryError(f"Erro ao deletar fila '{queue_name}'", delay=30)
