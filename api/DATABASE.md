# Configuração e Otimização do Banco de Dados SQLite

Este documento descreve as otimizações e melhorias implementadas no banco de dados SQLite do sistema EJC.

## 🚀 Melhorias Implementadas

### 1. WAL Mode (Write-Ahead Logging)
- **O que é**: Modo de journal que permite leituras simultâneas enquanto há escritas
- **Benefício**: Melhor concorrência e performance em operações simultâneas
- **Como funciona**: Escritas são registradas em um arquivo separado antes de serem aplicadas ao banco

### 2. Otimizações de Performance

#### Cache Size
- Cache de **64MB** em memória para reduzir I/O do disco
- Aumenta velocidade de consultas frequentes

#### Synchronous Mode
- Modo `NORMAL`: Balance entre segurança e performance
- Mais rápido que `FULL`, mas ainda seguro

#### Memory-Mapped I/O
- **256MB** de memória mapeada
- Permite que o SQLite acesse o banco diretamente da memória

#### Temp Store
- Armazenamento temporário em memória
- Reduz operações de disco para operações temporárias

### 3. Foreign Keys
- Habilita validação de chaves estrangeiras
- Mantém integridade referencial dos dados

## 📊 Funções de Manutenção

### Backup Automático
```python
from utils import backup_database

# Criar backup
backup_path = backup_database()
```

### Otimização
```python
from utils import optimize_database

# Compactar e otimizar banco
optimize_database()
```

### Informações do Banco
```python
from utils import get_database_info

# Obter informações
info = get_database_info()
print(info)
```

### Limpeza de Backups Antigos
```python
from utils import cleanup_old_backups

# Remover backups com mais de 30 dias
cleanup_old_backups(days_to_keep=30)
```

## 🔧 Rotas da API

### Informações do Banco
```
GET /api/db/info
```
Retorna informações sobre o banco de dados (tamanho, número de registros, etc.)

### Criar Backup
```
POST /api/db/backup
```
Cria um backup do banco de dados na pasta `data/backups/`

### Otimizar Banco
```
POST /api/db/optimize
```
Executa VACUUM e ANALYZE para otimizar o banco de dados

## 📝 Script de Manutenção

Execute o script de manutenção manualmente:

```bash
cd api
python -m utils.db_maintenance
```

Este script executa:
1. Exibe informações do banco
2. Cria um backup
3. Otimiza o banco de dados
4. Remove backups antigos (mais de 30 dias)

## 💡 Dicas de Uso

### Quando Otimizar
- Após deletar muitos registros
- Quando o banco ficar muito fragmentado
- Mensalmente como manutenção preventiva

### Quando Fazer Backup
- Antes de atualizações importantes
- Após grandes importações de dados
- Semanalmente como rotina

### Monitoramento
- Verifique o tamanho do banco periodicamente
- Monitore o número de backups na pasta `data/backups/`
- Use `/api/db/info` para acompanhar estatísticas

## 🔒 Segurança

- **Backups**: Armazenados em `data/backups/` com timestamp
- **Integridade**: Foreign keys habilitadas para validação
- **Durabilidade**: WAL mode garante que dados não sejam perdidos mesmo em caso de falha

## 📈 Performance Esperada

Com essas otimizações, você pode esperar:
- ✅ Até **10x** mais rápido em consultas frequentes
- ✅ Suporte a **múltiplas leituras simultâneas**
- ✅ Redução significativa de **I/O do disco**
- ✅ Melhor uso de **memória disponível**

## 🛠️ Configuração Avançada

Para ajustar as configurações, edite `api/database/database.py`:

```python
# Aumentar cache (padrão: 64MB)
cursor.execute("PRAGMA cache_size=-128000")  # 128MB

# Aumentar memory-mapped I/O (padrão: 256MB)
cursor.execute("PRAGMA mmap_size=536870912")  # 512MB
```

## 📚 Referências

- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [SQLite Performance Tuning](https://www.sqlite.org/performance.html)
- [SQLite PRAGMA](https://www.sqlite.org/pragma.html)
