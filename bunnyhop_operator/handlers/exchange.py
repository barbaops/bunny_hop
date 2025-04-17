import kopf
import aio_pika
import os
import base64
import kubernetes

from utils.rabbitmq_conn import RabbitMQConnectionFactory


@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'exchanges')
async def create_exchange(spec, namespace, logger, **kwargs):
    factory = RabbitMQConnectionFactory(namespace)
    connection = await factory.get_connection()
    channel = await connection.channel()

    exchange_name = spec['name']
    exchange_type = spec['type']
    durable = spec.get('durable', True)
    auto_delete = spec.get('autoDelete', False)

    await channel.declare_exchange(
        name=exchange_name,
        type=exchange_type,
        durable=durable,
        auto_delete=auto_delete,
    )
    await connection.close()
    logger.info(f"Exchange '{exchange_name}' created.")


@kopf.on.delete('rabbitmq.bruno.io', 'v1alpha1', 'exchanges')
async def delete_queue(spec, name, namespace, logger, **kwargs):
    factory = RabbitMQConnectionFactory(namespace)
    connection = await factory.get_connection()
    channel = await connection.channel()

    exchange_name = spec.get('name', name)

    try:
        await channel.exchange_delete(exchange_name)
        logger.info(f"Exchange '{exchange_name}' deleted.")
        await connection.close()
    except Exception as e:
        logger.error(f"Erro ao deletar exchange '{exchange_name}': {e}")
        raise kopf.TemporaryError(f"Erro ao deletar exchange '{exchange_name}'", delay=30)
