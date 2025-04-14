import base64
import kopf
import aio_pika
import os
import kubernetes

@kopf.on.create('rabbitmq.bruno.io', 'v1alpha1', 'queues')
async def create_queue(spec, name, namespace, logger, **kwargs):
    queue_name = spec.get('name', name)
    durable = spec.get('durable', True)
    auto_delete = spec.get('autoDelete', False)
    arguments = spec.get('arguments', {})

    rabbit_url = None
    connection = spec.get('connection', {})
    secret_ref = connection.get('secretRef', None)

    if secret_ref:
        secret_name = secret_ref.get('name')
        secret_key = secret_ref.get('key', 'uri')

        k8s_client = kubernetes.client.CoreV1Api()
        secret = k8s_client.read_namespaced_secret(secret_name, namespace)
        rabbit_url = base64.b64decode(secret.data[secret_key]).decode()
        logger.info(f"RabbitMQ URL loaded from SecretRef: {secret_name}/{secret_key}")
    else: 
        global_secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-rabbitmq-connection")
        global_secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")
        k8s_client = kubernetes.client.CoreV1Api()
        try:
            secret = k8s_client.read_namespaced_secret(global_secret_name, namespace)
            rabbit_url = base64.b64decode(secret.data[global_secret_key]).decode()
            logger.info(f"RabbitMQ URL loaded from global Secret: {global_secret_name}/{global_secret_key}")
        except Exception as e:
            raise kopf.PermanentError(f"Unable to load RabbitMQ URL from global Secret: {e}")

    if not rabbit_url:
        raise kopf.PermanentError("RabbitMQ connection URL could not be resolved.")

    connection = await aio_pika.connect_robust(rabbit_url)
    channel = await connection.channel()
    await channel.declare_queue(queue_name, durable=durable, auto_delete=auto_delete, arguments=arguments)
    await connection.close()

    logger.info(f"Queue '{queue_name}' created.")
    return {"queue": queue_name, "status": "created"}
