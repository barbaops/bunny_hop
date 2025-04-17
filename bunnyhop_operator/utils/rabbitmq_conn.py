import base64
import os
import aio_pika
import kubernetes


class RabbitMQConnectionFactory:

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.secret_name = os.getenv("RABBITMQ_CONN_SECRET_NAME", "bunnyhop-operator-con")
        self.secret_key = os.getenv("RABBITMQ_CONN_SECRET_KEY", "uri")

    def get_uri(self) -> str:
        k8s = kubernetes.client.CoreV1Api()
        secret = k8s.read_namespaced_secret(self.secret_name, self.namespace)
        return base64.b64decode(secret.data[self.secret_key]).decode()

    async def get_connection(self) -> aio_pika.RobustConnection:
        uri = self.get_uri()
        return await aio_pika.connect_robust(uri)
