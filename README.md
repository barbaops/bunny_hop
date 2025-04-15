# 🐰 BunnyHop Operator

![version](https://img.shields.io/badge/version-0.2.0-blue)
![status](https://img.shields.io/badge/status-active-brightgreen)
![license](https://img.shields.io/badge/license-MIT-yellow)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-supported-orange)
![Kubernetes](https://img.shields.io/badge/Kubernetes-CRD--based-blueviolet)

> Operator Kubernetes para criação e gerenciamento de recursos RabbitMQ via CRDs. Desenvolvido com 🧠 [Kopf](https://kopf.readthedocs.io) + 🐍 Python.

---

## ✨ Recursos Suportados

- ✅ Filas (`Queue` - _Alias rq_)
- ✅ Exchanges (`Exchange` - _Alias rx_)
- ✅ Bindings (`Binding` - _Alias rb_)
- ✅ Shovels (`Shovel` - _Alias rsh_)
- ✅ Exclusão automática com `kubectl delete`
- ✅ Conexão via `Secrets`

---

## 📦 Instalação

### Pré-requisitos

- Python 3.10+
- Kubernetes com `kubectl`
- RabbitMQ rodando (com plugins ativados: `management`, `shovel`, `shovel_management`)

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Aplique os CRDs

```bash
kubectl apply -f config/crd-queue.yaml
kubectl apply -f config/crd-exchange.yaml
kubectl apply -f config/crd-binding.yaml
kubectl apply -f config/crd-shovel.yaml
```

### 3. Crie o Secret com a URI de conexão

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: bunnyhop-rabbitmq-connection
  namespace: default
type: Opaque
stringData:
  uri: amqp://guest:guest@localhost:5672/
```

```bash
kubectl apply -f secret-rabbitmq.yaml
```

### 4. Execute o Operator localmente

```bash
$env:RABBITMQ_CONN_SECRET_NAME = "bunnyhop-rabbitmq-connection"
$env:RABBITMQ_CONN_SECRET_KEY = "uri"
kopf run --standalone bunnyhop_operator/main.py
```

---

## 🧪 Exemplos

### Queue

```yaml
apiVersion: rabbitmq.bruno.io/v1alpha1
kind: Queue
metadata:
  name: fila-notificacoes
spec:
  name: fila.notificacoes
  durable: true
  autoDelete: false
  arguments:
    x-message-ttl: 60000
```

### Exchange

```yaml
apiVersion: rabbitmq.bruno.io/v1alpha1
kind: Exchange
metadata:
  name: minha-exchange
spec:
  name: minha.exchange
  type: direct
  durable: true
  autoDelete: false
```

### Binding

```yaml
apiVersion: rabbitmq.bruno.io/v1alpha1
kind: Binding
metadata:
  name: bind-fila-notificacoes
spec:
  exchange: minha.exchange
  queue: fila.notificacoes
  routingKey: notificacoes
```

### Shovel (Exchange → Queue)

```yaml
apiVersion: rabbitmq.bruno.io/v1alpha1
kind: Shovel
metadata:
  name: shovel-ex-to-queue
spec:
  sourceURI: amqp://guest:guest@localhost:5672/
  sourceExchange: minha.exchange
  routingKey: notificacoes
  destinationURI: amqp://guest:guest@localhost:5672/
  destinationQueue: fila.destino
```

---

## 🧹 Exclusão automática

```bash
kubectl delete queue fila-notificacoes
```

> Remove também do RabbitMQ

---

## 🚀 Roadmap

- [x] Queue
- [x] Exchange
- [x] Binding
- [x] Shovel
- [ ] Helm Chart oficial
- [ ] VHost, Users, Policies
- [ ] Observabilidade Prometheus
- [ ] ArgoCD-ready

---

## 🛡️ Licença

MIT © 2025 - BunnyHop Project by [@bruno](https://github.com/seu-usuario)

# Created By
Wallace Bruno Gentil - Chwiee
