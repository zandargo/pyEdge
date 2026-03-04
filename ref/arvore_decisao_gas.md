# Arvore de Decisao de Selecao de Gas

Fonte: `ui/components/calculators_panel.py` (`select_assist_gas`)

## Entradas

- `material`: `carbon_steel | stainless_steel | galvanized_steel | aluminum | other`
- `thickness_mm`: espessura numerica em mm
- `edge_quality`: `high | medium | low`
- `post_process`: `none | welding | painting`
- `cost_priority`: `true | false`

Flag derivada usada pelo algoritmo:

- `avoid_oxygen = (post_process in [welding, painting])`

## Arvore de Decisao Completa

```text
INICIO
|
+-- Calcular avoid_oxygen = (post_process e welding ou painting)
|
+-- material == carbon_steel?
|   |
|   +-- SIM
|   |   |
|   |   +-- thickness_mm > 12?
|   |   |   |
|   |   |   +-- SIM
|   |   |   |   |
|   |   |   |   +-- avoid_oxygen == true?
|   |   |   |       |
|   |   |   |       +-- SIM -> GAS = nitrogen
|   |   |   |       |         Motivo: Carbono espesso normalmente usa oxigenio,
|   |   |   |       |         mas solda/pintura exige bordas sem oxidacao.
|   |   |   |       |
|   |   |   |       +-- NAO -> GAS = oxygen
|   |   |   |                 Motivo: Em aco carbono pesado, o oxigenio adiciona
|   |   |   |                 energia exotermica para corte em toda a espessura.
|   |   |   |
|   |   |   +-- NAO
|   |   |       |
|   |   |       +-- thickness_mm <= 3?
|   |   |           |
|   |   |           +-- SIM
|   |   |           |   |
|   |   |           |   +-- avoid_oxygen == true E cost_priority == true?
|   |   |           |   |   |
|   |   |           |   |   +-- SIM -> GAS = compressed_air
|   |   |           |   |   |         Motivo: Chapa fina + pos-processo +
|   |   |           |   |   |         prioridade de custo favorece ar comprimido.
|   |   |           |   |   |
|   |   |           |   |   +-- NAO
|   |   |           |   |       |
|   |   |           |   |       +-- edge_quality == high?
|   |   |           |   |           |
|   |   |           |   |           +-- SIM -> GAS = nitrogen
|   |   |           |   |           |         Motivo: Alta qualidade de borda em
|   |   |           |   |           |         chapa fina de carbono pede corte sem oxidacao.
|   |   |           |   |           |
|   |   |           |   |           +-- NAO
|   |   |           |   |               |
|   |   |           |   |               +-- cost_priority == true?
|   |   |           |   |                   |
|   |   |           |   |                   +-- SIM -> GAS = compressed_air
|   |   |           |   |                   |         Motivo: Reducao de custo priorizada.
|   |   |           |   |                   |
|   |   |           |   |                   +-- NAO -> GAS = compressed_air
|   |   |           |   |                             Motivo: Padrao para carbono fino,
|   |   |           |   |                             qualidade aceitavel com baixo custo.
|   |   |           |
|   |   |           +-- NAO (isso significa 3 < thickness_mm <= 12)
|   |   |               |
|   |   |               +-- avoid_oxygen == true?
|   |   |                   |
|   |   |                   +-- SIM -> GAS = nitrogen
|   |   |                   |         Motivo: Pos-processo exige bordas sem oxidacao.
|   |   |                   |
|   |   |                   +-- NAO -> GAS = oxygen
|   |   |                             Motivo: Aco carbono medio se beneficia do
|   |   |                             suporte exotermico do oxigenio.
|   |
|   +-- NAO
|       |
|       +-- material == stainless_steel?
|       |   |
|       |   +-- SIM
|       |   |   |
|       |   |   +-- cost_priority == true E thickness_mm <= 3 E avoid_oxygen == false?
|       |   |       |
|       |   |       +-- SIM -> GAS = compressed_air
|       |   |       |         Motivo: Inox fino com prioridade de custo pode usar ar
|       |   |       |         com qualidade razoavel.
|       |   |       |
|       |   |       +-- NAO -> GAS = nitrogen
|       |   |                 Motivo: Inox geralmente exige bordas limpas,
|       |   |                 sem oxidacao e prontas para solda.
|       |
|       +-- NAO
|           |
|           +-- material == galvanized_steel?
|           |   |
|           |   +-- SIM
|           |   |   |
|           |   |   +-- thickness_mm <= 3?
|           |   |       |
|           |   |       +-- SIM -> GAS = compressed_air
|           |   |       |         Motivo: Galvanizado fino pode usar ar para
|           |   |       |         diluir fumos de zinco e reduzir custo.
|           |   |       |
|           |   |       +-- NAO -> GAS = nitrogen
|           |   |                 Motivo: Em maior espessura, nitrogenio reduz
|           |   |                 fumos de oxido de zinco e melhora borda.
|           |
|           +-- NAO
|               |
|               +-- material == aluminum?
|               |   |
|               |   +-- SIM
|               |   |   |
|               |   |   +-- thickness_mm > 6?
|               |   |       |
|               |   |       +-- SIM -> GAS = nitrogen
|               |   |       |         Motivo: Aluminio espesso precisa de gas inerte
|               |   |       |         para evitar oxidacao e ajudar na expulsao do fundido.
|               |   |       |
|               |   |       +-- NAO -> GAS = nitrogen
|               |   |                 Motivo: Aluminio em geral requer gas inerte
|               |   |                 para evitar formacao de oxido e manter borda limpa.
|               |
|               +-- NAO -> GAS = nitrogen
|                         Motivo: Fallback padrao (opcao inerte mais segura).
```

## Lista Compacta de Regras

1. Aco carbono, `thickness_mm > 12`
- `avoid_oxygen=true` -> `nitrogen`
- `avoid_oxygen=false` -> `oxygen`

2. Aco carbono, `thickness_mm <= 3`
- `avoid_oxygen=true` e `cost_priority=true` -> `compressed_air`
- senao se `edge_quality=high` -> `nitrogen`
- senao se `cost_priority=true` -> `compressed_air`
- senao -> `compressed_air`

3. Aco carbono, `3 < thickness_mm <= 12`
- `avoid_oxygen=true` -> `nitrogen`
- `avoid_oxygen=false` -> `oxygen`

4. Aco inoxidavel
- `cost_priority=true` e `thickness_mm <= 3` e `avoid_oxygen=false` -> `compressed_air`
- senao -> `nitrogen`

5. Aco galvanizado
- `thickness_mm <= 3` -> `compressed_air`
- `thickness_mm > 3` -> `nitrogen`

6. Aluminio
- Sempre `nitrogen` (o codigo separa mensagens para `> 6` e `<= 6`)

7. Material desconhecido
- Padrao -> `nitrogen`

## Resumo de Saidas

- `oxygen` aparece apenas em caminhos de aco carbono quando nao ha restricao explicita ao oxigenio.
- `compressed_air` aparece principalmente em chapas finas e/ou decisoes com foco em custo.
- `nitrogen` e a opcao inerte dominante para qualidade, anti-oxidacao e fallback seguro.
