import kopf
import aio_pika
import os
import base64
import kubernetes

from utils.rabbitmq_conn import RabbitMQConnectionFactory


@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'bindings')
async def create_binding(spec, namespace, logger, **kwargs):
    factory = RabbitMQConnectionFactory(namespace)
    connection = await factory.get_connection()
    channel = await connection.channel()

    exchange_name = spec['exchange']
    queue_name = spec['queue']
    routing_key = spec['routingKey']

    exchange = await channel.get_exchange(exchange_name)
    queue = await channel.get_queue(queue_name)

    await queue.bind(exchange, routing_key=routing_key)

    await connection.close()
    logger.info(f"Bound queue '{queue_name}' to exchange '{exchange_name}' with key '{routing_key}'.")

    
@kopf.on.delete('rabbitmq.bruno.io', 'v1alpha1', 'bindings')
async def delete_binding(spec, name, namespace, logger, **kwargs):
    factory = RabbitMQConnectionFactory(namespace)
    connection = await factory.get_connection()
    channel = await connection.channel()

    exchange = spec["exchange"]
    queue = spec["queue"]
    routing_key = spec["routingKey"]

    try:
        exchange_obj = await channel.get_exchange(exchange)
        queue_obj = await channel.get_queue(queue)

        await queue_obj.unbind(exchange_obj, routing_key=routing_key)
        await connection.close()

        logger.info(f"Binding '{queue}' ← '{exchange}' com routing key '{routing_key}' removido.")
    except Exception as e:
        logger.error(f"Erro ao remover binding '{queue}' de '{exchange}': {e}")
        raise kopf.TemporaryError(f"Erro ao remover binding '{queue}' de '{exchange}'", delay=30)
