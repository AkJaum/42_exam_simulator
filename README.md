# 42 Exam Simulator

Simulador terminal-first para praticar exams da 42. O fluxo tenta reproduzir a experiencia do exame: o aluno recebe um subject sorteado, resolve dentro de `rendu/`, volta ao terminal principal e usa `grademe` para corrigir. A proxima questao so aparece depois de passar nos testes da atual.

## Requisitos

- Linux
- Bash
- Python 3.10+
- `cc` para questoes em C

Nao ha dependencias Python externas.

## Como rodar

```bash
make run
```

O comando vai pedir:

1. Login do aluno.
2. Exame a simular.
3. Modalidade.

Ao iniciar, ele cria uma pasta de sessao no diretorio do projeto:

```text
exam_<login>_<data_hora>/
  subjects/
  rendu/
  traces/
  session.json
```

Mantenha o terminal do `make run` aberto durante o simulado. Use o terminal da sessao ou seu editor para criar a pasta da questao e os arquivos dentro de `rendu/<questao>/`.

Em um terminal interativo, o prompt mostra o tempo restante ao vivo enquanto voce digita. As mensagens usam cores ANSI automaticamente; defina `NO_COLOR=1` se quiser desativar cores.

Quando possivel, o simulador abre automaticamente um segundo terminal dentro da raiz da sessao `exam_<login>_<data_hora>/`. Esse suporte e feito em modo best effort para Linux: ele tenta abrir uma nova janela em `tmux` ou `screen` quando estiver dentro desses ambientes; em sessoes graficas, tenta `EXAM_SIM_TERMINAL`, `TERMINAL`, `xdg-terminal-exec`, `x-terminal-emulator` e emuladores comuns como GNOME Terminal, Konsole, XFCE Terminal, Kitty, Alacritty, WezTerm, xterm e outros. Se estiver sem sessao grafica, fora de `tmux/screen`, em SSH simples, ou sem terminal conhecido instalado, o simulado continua normalmente e mostra o comando `cd` para abrir manualmente.

Variaveis uteis:

- `EXAM_SIM_NO_TERMINAL=1`: nao tenta abrir outro terminal automaticamente.
- `EXAM_SIM_TERMINAL`: define o terminal preferido. Use `{cwd}` se quiser controlar onde o caminho da sessao entra no comando.

## Comandos do terminal principal

- `grademe`: corrige a questao atual.
- `status`: mostra tempo restante, questao atual, valor da questao e score.
- `subject`: mostra o caminho do subject atual.
- `terminal`: tenta abrir outro terminal na raiz da sessao.
- `help`: mostra os comandos disponiveis.
- `exit`: encerra o simulado manualmente.

## Modalidades

### 1 - Simulador real do exame

Mostra score no formato `pontos/100`. A questao atual pode ser tentada quantas vezes forem necessarias ate passar ou ate acabar o tempo. A simulacao termina quando o aluno chega em `100/100`, quando o tempo acaba, ou quando nao ha mais questoes disponiveis.

### 2 - Simulador mata-mata

Mostra score no formato `pontos/soma_de_todos_os_pontos_do_exame`. Sorteia questoes continuamente sem repetir. Se uma correcao falhar, o simulado termina imediatamente. Se o aluno acertar tudo, termina ao atingir a pontuacao maxima do exame.

## Timer

Cada sessao tem 3 horas. O tempo e controlado pelo processo Python que fica aberto no terminal principal, e o prompt redesenha o contador regressivo em tempo real. O estado atual tambem fica salvo em `session.json`.

## Como adicionar novas questoes

Crie uma pasta em `questions/<exam>/<nome_da_questao>/`:

```text
questions/
  exam_rank_02/
    ft_strlen/
      subject.txt
      meta.json
      tests/
        test.sh
```

Exemplo de `meta.json`:

```json
{
  "name": "ft_strlen",
  "language": "c",
  "points": 10,
  "required_files": ["ft_strlen.c"],
  "allowed_functions": [],
  "forbidden_functions": [],
  "test_command": "bash tests/test.sh",
  "timeout_seconds": 10
}
```

Campos importantes:

- `name`: nome da pasta esperada dentro de `rendu/`.
- `points`: pontuacao da questao.
- `required_files`: arquivos obrigatorios dentro de `rendu/<name>/`.
- `test_command`: comando executado a partir da pasta da questao.
- `timeout_seconds`: limite de tempo para os testes da questao.

## Como criar testes

O `test.sh` roda com estas variaveis de ambiente:

- `RENDU_DIR`: caminho absoluto para `exam_.../rendu`.
- `ANSWER_DIR`: caminho absoluto para `exam_.../rendu/<questao>`.
- `QUESTION_NAME`: nome da questao atual.

O teste deve retornar exit code `0` para sucesso e diferente de `0` para falha. Tudo que for impresso em stdout/stderr sera salvo em `traces/`.

Durante a sessao, `subjects/` acumula os subjects ja sorteados usando o nome da questao, por exemplo `subjects/bracket_validator.txt`. A pasta da resposta nao e criada automaticamente dentro de `rendu/`; o aluno deve cria-la como no exame real.

Os testes podem emitir casos estruturados com `TRACE_CASE`. Quando isso existe, o trace do `grademe` lista cada caso testado como `OK` ou `DIFF_KO`. Em falhas, input, esperado e recebido aparecem mascarados por hash curto para indicar divergencia sem entregar a resposta direta.

## Questoes de exemplo

Esta versao inclui exemplos suficientes para validar o fluxo:

- `exam_rank_03/bracket_validator`

## Validacao local

```bash
make check
```

Esse comando compila os arquivos Python e valida os JSONs das questoes.

## Limpeza

```bash
make clean
```

Remove sessoes antigas `exam_<login>_<data_hora>/`, caches Python e temporarios comuns criados durante desenvolvimento ou testes.
