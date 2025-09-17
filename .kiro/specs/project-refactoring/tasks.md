# Implementation Plan

- [x] 1. Preparar ambiente e estrutura inicial

  - Criar a nova estrutura de diretórios conforme o design
  - Configurar arquivos **init**.py para todos os pacotes
  - _Requirements: 1.1, 1.4_

- [x] 2. Consolidar código legado

  - [x] 2.1 Analisar e catalogar arquivos nas pastas archive/, legacy/ e core/

    - Identificar arquivos duplicados e versões mais recentes
    - Documentar dependências entre arquivos
    - _Requirements: 2.1, 2.2_

  - [x] 2.2 Criar pasta archive/ unificada

    - Mover todos os arquivos legados para a pasta archive/
    - Criar README.md na pasta archive/ explicando o conteúdo
    - _Requirements: 2.1, 2.4_

- [ ] 3. Implementar camada de modelos

  - [x] 3.1 Criar modelos de dados básicos

    - Implementar modelo Prospect
    - Implementar modelo QualifiedProspect
    - Implementar modelo LeakResult
    - _Requirements: 3.1, 3.2_

  - [x] 3.2 Implementar interfaces base

    - Criar interface Pipeline
    - Criar interface Engine
    - Criar interface Integration
    - _Requirements: 3.1, 3.2, 3.3_

- [ ] 4. Implementar camada de engines

  - [x] 4.1 Migrar SimplifiedEngine

    - Refatorar código do SimplifiedProductionEngine
    - Adaptar para a nova estrutura de interfaces
    - _Requirements: 3.1, 6.1_

  - [x] 4.2 Migrar DiscoveryEngine

    - Refatorar código do RealDiscoveryEngine
    - Adaptar para a nova estrutura de interfaces
    - _Requirements: 3.1, 6.1, 6.2_

  - [x] 4.3 Migrar LeakEngine

    - Refatorar código do RealLeakDetector
    - Adaptar para a nova estrutura de interfaces
    - _Requirements: 3.1, 6.1, 6.2_

  - [x] 4.4 Migrar ValidatorEngine

    - Refatorar código do ValidatorEngine
    - Adaptar para a nova estrutura de interfaces
    - _Requirements: 3.1, 6.1_

- [ ] 5. Implementar camada de integração

  - [x] 5.1 Criar adaptadores para APIs externas

    - Implementar integração com Wappalyzer
    - Implementar integração com Google APIs
    - _Requirements: 3.1, 6.2_

  - [x] 5.2 Implementar mecanismos de retry e fallback

    - Criar sistema de retry para chamadas de API
    - Implementar fallbacks para quando APIs não estão disponíveis
    - _Requirements: 3.1, 6.2_

- [x] 6. Implementar camada de configuração

  - [x] 6.1 Centralizar configurações

    - Criar sistema de carregamento de configurações
    - Migrar configurações existentes para o novo formato
    - _Requirements: 5.1, 5.2_

  - [x] 6.2 Implementar gerenciamento de variáveis de ambiente

    - Criar .env.template com todas as variáveis necessárias
    - Implementar carregamento de variáveis de ambiente
    - _Requirements: 5.2, 5.4_

- [x] 7. Implementar camada de pipelines

  - [x] 7.1 Refatorar StandardPipeline

    - Adaptar para usar os novos engines
    - Garantir compatibilidade com a interface CLI existente
    - _Requirements: 3.1, 6.1, 6.3_

  - [x] 7.2 Refatorar AdvancedPipeline

    - Adaptar para usar os novos engines e integrações
    - Garantir compatibilidade com a interface CLI existente
    - _Requirements: 3.1, 6.1, 6.2, 6.3_

- [x] 8. Atualizar ponto de entrada principal

  - Refatorar main.py para usar os novos pipelines
  - Garantir compatibilidade com os comandos CLI existentes
  - _Requirements: 3.4, 6.3_

- [x] 9. Consolidar e atualizar testes

  - [x] 9.1 Migrar testes existentes

    - Consolidar testes em uma estrutura unificada
    - Adaptar testes para a nova estrutura de código
    - _Requirements: 2.3, 3.3, 6.4_

  - [x] 9.2 Implementar novos testes

    - Criar testes unitários para novos componentes
    - Implementar testes de integração para fluxos principais
    - _Requirements: 3.3, 6.4_

- [ ] 10. Atualizar documentação

  - [x] 10.1 Consolidar documentação existente

    - Mover documentação relevante para a pasta docs/
    - Remover documentação obsoleta
    - _Requirements: 4.1_

  - [x] 10.2 Criar nova documentação

    - Atualizar README.md principal
    - Criar guias de instalação, uso e contribuição
    - Documentar a nova arquitetura
    - _Requirements: 4.2, 4.3, 4.4_

- [x] 11. Limpar arquivos temporários e de debug

  - Identificar e remover arquivos temporários
  - Remover código de debug não essencial
  - _Requirements: 2.4_

- [ ] 12. Validação final

  - Executar testes completos
  - Verificar compatibilidade com comandos CLI existentes
  - Validar que todos os requisitos foram atendidos
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [-] 13. Implementar módulo de ICP (Ideal Customer Profile)

  - [x] 13.1 Criar modelo de dados para ICPs

    - Implementar modelo para Shopify DTC Premium (Skincare/Beauty)
    - Implementar modelo para Subscription E-commerce (Coffee/Snacks)
    - Implementar modelo para Course Creators at Scale
    - _Requirements: 3.1, 3.2_

  - [x] 13.2 Implementar sistema de scoring para ICPs

    - Criar algoritmo de pontuação baseado em footprints técnicos
    - Implementar detecção de SaaS waste específico por ICP
    - Implementar cálculo de ROI esperado por ICP
    - _Requirements: 3.1, 6.1_

  - [x] 13.3 Integrar ICPs com o pipeline de descoberta

    - Adaptar DiscoveryEngine para filtrar por ICP
    - Implementar seed generation por ICP
    - Criar relatórios específicos por ICP
    - _Requirements: 3.1, 6.1, 6.2_

- [ ] 14. Implementar módulo de proposta de valor

  - [x] 14.1 Criar sistema de detecção de vazamentos financeiros

    - Implementar detecção de apps redundantes
    - Implementar análise de performance vs. conversão
    - Implementar cálculo de savings verificados
    - _Requirements: 3.1, 6.1_

  - [x] 14.2 Implementar geração de relatórios de ROI

    - Criar templates para "14-Day Revenue Recovery Pilot"
    - Implementar cálculo de savings projetados
    - Implementar visualização de performance vs. competidores
    - _Requirements: 3.1, 6.1_

  - [x] 14.3 Implementar sistema de outreach automatizado

    - Criar templates de email personalizados por ICP
    - Implementar geração de dashboards para prospectos
    - Integrar com ferramentas de outreach
    - _Requirements: 3.1, 6.2_
