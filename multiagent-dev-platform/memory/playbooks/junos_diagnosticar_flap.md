Diagnosticar e corrigir problemas de "flapping" (oscilação) no protocolo BGP em um equipamento Juniper MX201
envolve uma série de passos. Este playbook fornecerá orientações detalhadas sobre como identificar, diagnosticar e
resolver essas oscilações.

### Playbook: Diagnóstico de Flapping em Sessão BGP do Juniper MX201

#### 1. Pré-requisitos
- Acesso SSH ou Consola ao equipamento Juniper MX201.
- Privilegios de administrador para realizar as configurações necessárias.

#### 2. Passo a Passo

##### 2.1. Verificar Status Atual da Sessão BGP
```shell
show bgp neighbors
```

Este comando exibirá o status atual das sessões BGP, incluindo endereços IP dos peers, status (up/down), last
event e mais.

##### 2.2. Verificar Logs de Sessão BGP
```shell
show log | match "BGP"
```

Este comando exibirá os logs recentes relacionados ao BGP, incluindo eventos que podem indicar oscilações.

##### 2.3. Verificar Configuração do BGP
```shell
show configuration routing-options
```
Este comando exibirá a configuração atual do roteador, permitindo verificar os intervalos de holdtime e
retransmissão (keepalive).

##### 2.4. Verificar Conexão Física e Mídia
```shell
show interfaces terse
```

Verifique o status das interfaces físicas envolvidas na sessão BGP para descartar problemas de infraestrutura.

##### 2.5. Verificar Confiabilidade de Tempo
```shell
show system time
```

Certifique-se de que os relógios no sistema estejam sincronizados e consistentes.

##### 2.6. Configuração de Mínimos e Máximos para Flapping
Se a oscilação estiver causada por parâmetros configurados baixos, ajuste-os conforme necessário:
```shell
set routing-options autonomous-system <numero_as>
set routing-options bgp peer-group <nome_do_peer_group> hold-time <novo_holdtime> keepalive-interval
<novo_keepalive>
```
Substitua `<numero_as>` pelo número do seu autoidentificador AS, e ajuste os novos valores para `hold-time` e
`keepalive-interval`.

##### 2.7. Monitorar o Impacto da Mudança
Após fazer as alterações, continue monitorando o estado das sessões BGP por um período considerável:
```shell
show bgp neighbors
```
Acompanhe se a mudança mitigou ou resolveu o problema.

##### 2.8. Documentação e Revisão de Configuração
Documente as alterações realizadas, bem como os resultados obtidos. Revise periodicamente as configurações BGP
para garantir que elas ainda sejam adequadas.

### Recursos Adicionais

- **Guia do Usuário** do Juniper MX201 para referência completa.
- **Documentação da Juniper Networks** sobre o protocolo BGP e a configuração avançada.

### Conclusão
Este playbook fornece um passo a passo para diagnosticar e resolver problemas de flapping em sessões BGP no
Juniper MX201. Cada etapa deve ser executada cuidadosamente, e as mudanças devem ser monitoradas ativamente até
que o problema seja resolvido ou mitigado.

Se as oscilações persistirem após essas medidas, pode ser necessário investigar fatores externos à configuração do
BGP.

