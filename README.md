# 🐰 BunnyHop Operator

![version](https://img.shields.io/badge/version-0.2.0-blue)
![status](https://img.shields.io/badge/status-active-brightgreen)
![license](https://img.shields.io/badge/license-MIT-yellow)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-supported-orange)
![Kubernetes](https://img.shields.io/badge/Kubernetes-CRD--based-blueviolet)

> Operator Kubernetes para criação e gerenciamento de recursos RabbitMQ via CRDs. Desenvolvido com 🧠 [Kopf](https://kopf.readthedocs.io) + 🐍 Python.

---

## ✨ Recursos Suportados

- ✅ Filas (`Queue`)
- ✅ Exchanges (`Exchange`)
- ✅ Bindings (`Binding`)
- ✅ Shovels (`Shovel`)
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

# 🗺️ BunnyHop Operator – Roadmap Técnico

Este roadmap apresenta as funcionalidades planejadas para evolução do projeto.

---

## ✅ Versão Atual – `v0.1.0`

- [x] Criação de filas (`Queue`)
- [x] Criação de exchanges (`Exchange`)
- [x] Criação de bindings (`Binding`)
- [x] Criação de shovels (`Shovel`)
- [x] Deleção de todos os recursos
- [x] Helm Chart inicial
- [x] Suporte a conexão via Secret
- [x] Lógica de sincronização com verificação básica (em desenvolvimento)

---

## 🚀 `v0.2.0` – Validações e observabilidade

- [ ] ✅ Validações via JSONSchema no CRD (ex: TTL mínimo/máximo, nomes válidos)
  - [x] Queue
  - [] Exchange
  - [] Binding
  - [] Shovel
- [ ] ✅ Atualização de Recursos via `@kopf.on.update`
- [ ] ✅ Exibição do campo `SYNC` ao rodar `kubectl get`
- [ ] 🔍 Integração com RabbitMQ Management API para exibir dados como por exemplo:
  - TTL real
  - Número de mensagens
  - Quantidade de consumers
- [ ] 🎯 Implementar métricas Prometheus:
  - `bunnyhop_queue_created_total`
  - `bunnyhop_queue_sync_status{status="synced"}`
- [ ] 📢 Adicionar eventos no recurso (`kubectl describe`)

---

## 🛠️ `v0.3.0` – Auto-healing e controle granular

- [ ] 🔁 Auto-healing: se estiver fora de sync, recriar o recurso com a configuração correta
- [ ] 🔐 Suporte a múltiplos Secrets/vhosts por Namespace
- [ ] 🔒 Controle de acesso baseado em Namespace (RBAC + Policy de criação)

---

## 🎛️ `v0.4.0` – Templates e componentes avançados

- [ ] 📦 `QueueTemplate` e `ExchangeTemplate` reutilizáveis
- [ ] 🔁 Suporte a políticas DLQ, Retry e TTL Chains
- [ ] ✏️ Possibilidade de `annotations` como `bunnyhop.io/skip-if-exists`

---

## 🌍 `v1.0.0` – Pronto para produção

- [ ] CLI opcional: `kubectl bunnyhop`
- [ ] Documentação pública com exemplos completos
- [ ] Validação contínua em CI/CD (GitHub Actions)
- [ ] Upload do Helm Chart no ArtifactHub
- [ ] Suporte a Federation Links e Peerings RabbitMQ (opcional)

---

> 💬 Contribuições e sugestões são bem-vindas! [Abra um issue ou envie um PR 🚀](https://github.com/seuprojeto/bunnyhop)


---

## 🛡️ Licença

MIT © 2025 - BunnyHop Project by [@bruno](https://github.com/barbaops)
