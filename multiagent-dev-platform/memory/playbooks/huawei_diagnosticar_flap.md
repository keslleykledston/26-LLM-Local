### Playbook: Diagnóstico de Flapping em Sessão BGP do Huawei NE8000

#### 1. Pré-requisitos
- Acesso SSH ou Consola ao equipamento Huawei NE8000.
- Privilegios de administrador para realizar as configurações necessárias.

#### 2. Passo a Passo

##### 2.1. Verificar Status Atual da Sessão BGP
```shell
display bgp peer-group <nome_do_peer_group> brief
```
Substitua `<nome_do_peer_group>` pelo nome do grupo de peers relevantes, se aplicável.

A saída fornecerá um resumo das sessões BGP atuais, incluindo status (up/down) e outros detalhes. Procure por
sessões que estejam oscilando (status entre up/down).

##### 2.2. Verificar o Log de Sessão BGP
```shell
display logbuffer | include <peer_ip>
```
Substitua `<peer_ip>` pelo endereço IP do peer suspeito.

Este comando exibirá os logs recentes relacionados ao peer especificado, incluindo eventos que podem indicar
oscilações.

##### 2.3. Verificar Configuração de BGP
```shell
display bgp group <nome_do_peer_group>
```
Repetir para diferentes grupos de peers conforme necessário.

Este comando fornecerá detalhes sobre a configuração do peer, incluindo os intervalos de holdtime e retransmissão
(keepalive). Oscilações podem ser indicadas por valores muito baixos nesses parâmetros.

##### 2.4. Verificar Conexão Física e Mídia
```shell
display interface <interface_id>
```
Substitua `<interface_id>` pelo ID da interface de rede envolvida no peer.

Verifique a conectividade física e o status do mídia na interface em questão para descartar problemas de
infraestrutura como causa das oscilações.

##### 2.5. Verificar Confiabilidade de Tempo
```shell
display clock
```

Certifique-se de que os relógios nas redes envolvidas estejam sincronizados e consistentes, pois problemas com
horários podem causar flaps.

##### 2.6. Configuração de Mínimos e Maximos para Flapping
Se a oscilação estiver causada por parâmetros configurados baixos:
```shell
undo bgp <as> timer <holdtime> <keepalive>
bgp <as> timer <new_holdtime> <new_keepalive>
```
Substitua `<as>` pelo número do autoidentificador AS, e ajuste os novos valores para holdtime e keepalive
apropriados.

##### 2.7. Monitorar o Impacto da Mudança
Depois de fazer as alterações, continue monitorando o estado das sessões BGP por um período considerável:
```shell
display bgp peer-group <nome_do_peer_group> brief
```
Acompanhe se a mudança mitigou ou resolveu o problema.

##### 2.8. Documentação e Revisão de Configuração
Documente as alterações realizadas, bem como os resultados obtidos. Revise periodicamente as configurações BGP
para garantir que elas ainda sejam adequadas.

#### 3. Recursos Adicionais

- **Guia do Usuário** do Huawei NE8000 para referência completa.
- **Documentação da Huawei** sobre o protocolo BGP e a configuração avançada.

### Conclusão
Este playbook fornecê um passo a passo para diagnosticar e resolver problemas de flapping em sessões BGP no Huawei
NE8000. Cada etapa deve ser executada cuidadosamente, e as mudanças devem ser monitoradas ativamente até que o
problema seja resolvido ou mitigado.

Se as oscilações persistirem após essas medidas, pode ser necessário investigar fatores externos à configuração do
BGP.

