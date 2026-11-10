# Painel do ágio do dólar digital

Página pública com o ágio diário do USDT em reais sobre a PTAX, medido em dois horários:

- **Janela da PTAX (10h–13h de Brasília):** a medida principal do TCC.
- **Fechamento (21h, 00:00 UTC):** o horário das bases de criptoativos, para comparação.

**Acesse: [augustojrezende.github.io/agio-painel](https://augustojrezende.github.io/agio-painel/)**

A página explica em um minuto o que são USDT, PTAX e ágio; mostra o valor do último dia útil com uma frase de leitura, a série desde outubro de 2020, por que os dois horários dão leituras diferentes (com o exemplo de 09/04/2025), os dias em que as duas medidas mais divergiram, a metodologia, o que o painel não diz e um glossário.

Projeto de origem (código, pré-registro e resultados): [augustojrezende/agio-stablecoin](https://github.com/augustojrezende/agio-stablecoin).

## Separação do projeto de origem

Este repositório **não altera** o `agio-stablecoin`. A versão congelada para a validação (tag `congelamento-v2`) fica intacta. O painel só lê dois arquivos que o comando `agio calcular` já grava:

| Arquivo de origem | Conteúdo |
| --- | --- |
| `dados/tratado/agio_diario.csv` | Ágio na janela da PTAX |
| `dados/tratado/agio_fechamento_diario.csv` | Ágio no fechamento |

O painel publica **só o nível do ágio**. Não mostra regressões, estudos de evento nem decisões sobre as hipóteses, que continuam restritas às datas do pré-registro (out/2027 descritiva e out/2028 decisão).

## Arquivos

| Arquivo | Papel |
| --- | --- |
| `favicon.svg` | Ícone da aba |
| `index.html` | A página (HTML, CSS e JavaScript num só arquivo; gráfico com Chart.js 4.4.1 por CDN) |
| `dados/agio.json` | Série gerada pelo exportador; não editar à mão |
| `dados/episodios.json` | Notas de contexto dos dias de divergência já verificados (editado à mão, com fonte) |
| `scripts/exportar.py` | Lê os CSVs do projeto de origem e grava `dados/agio.json` (só biblioteca padrão) |
| `scripts/agendar_mac.sh` | Agenda a exportação no Mac: roda quando o ágio é recalculado, com reserva às terças 10h |
| `tests/test_exportar.py` | Testes do exportador com dados sintéticos |

## Como usar

Pré-requisito: este repositório clonado **ao lado** do projeto de origem (`~/Projetos/agio-painel` e `~/Projetos/agio-stablecoin`).

```bash
cd ~/Projetos/agio-painel
python3 scripts/exportar.py                # gera dados/agio.json
python3 scripts/exportar.py --publicar     # gera, faz commit e push se mudou
./scripts/agendar_mac.sh                   # roda sempre que a coleta recalcula o ágio
python3 -m pytest -q tests                 # 8 testes, sem rede
```

Com `--publicar`, o exportador atualiza o clone (`git pull`), espera os CSVs de origem ficarem 60 segundos sem mudar e só publica se houver dia novo.

Para ver a página no próprio computador: `python3 -m http.server` e abrir `http://localhost:8000`.

## Publicação

GitHub Pages, a partir da branch `main`, pasta raiz (Settings → Pages). Endereço: `https://augustojrezende.github.io/agio-painel/`. Sem servidor e sem custo.

## Episódios

Uma nota só entra em `dados/episodios.json` quando o dia foi verificado (horário da notícia contra a janela da PTAX), com a mesma fonte usada no artigo. Os demais dias de divergência aparecem na tabela sem comentário.

## Licenças

- Código: MIT (`LICENSE`).
- Série publicada (`dados/agio.json`): CC BY-NC-SA 4.0 (`LICENSE-DADOS.md`). A licença é mais restritiva que a do projeto de origem por prudência com os termos de uso dos dados da Binance.
