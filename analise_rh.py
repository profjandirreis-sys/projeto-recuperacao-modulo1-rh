"""
Projeto de Recuperação - Módulo 1 (SCTEC / SENAI-SC)
Análise Exploratória de Dados (EDA) - Recursos Humanos (esquema HR do FreeSQL)
Aluno: Jandir Medeiros dos Reis

Como executar:
    pip install -r requirements.txt
    python analise_rh.py

Entradas : data/query_01.csv e data/query_02.csv (exportados do FreeSQL)
Saídas   : gráficos na pasta imagens/ e resumo impresso no terminal
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # salva os gráficos em arquivo, sem abrir janela
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parent
DADOS = BASE / "data"
IMAGENS = BASE / "imagens"
IMAGENS.mkdir(exist_ok=True)

warnings.filterwarnings("ignore", category=matplotlib.MatplotlibDeprecationWarning)

COR = "#2E6DB4"
COR_DESTAQUE = "#D9534F"


def titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def moeda(valor):
    return f"US$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# 1. Carregar os dados
# ---------------------------------------------------------------------------
q1 = pd.read_csv(DADOS / "query_01.csv")  # salários x departamento x cargo
q2 = pd.read_csv(DADOS / "query_02.csv")  # funcionários x cidade x país x região
q1["department_id"] = q1["department_id"].astype("Int64")  # inteiro que aceita nulo

titulo("1. VISÃO GERAL DOS DADOS")
print(f"query_01.csv: {q1.shape[0]} linhas x {q1.shape[1]} colunas")
print(f"query_02.csv: {q2.shape[0]} linhas x {q2.shape[1]} colunas")
print("\nPrimeiras linhas da Query 1:")
print(q1.head().to_string(index=False))
print("\nTipos de dados da Query 1:")
print(q1.dtypes.to_string())

# ---------------------------------------------------------------------------
# 2. Qualidade dos dados: nulos e duplicados
# ---------------------------------------------------------------------------
titulo("2. QUALIDADE DOS DADOS")
print("Valores nulos por coluna (Query 1):")
print(q1.isna().sum()[lambda s: s > 0].to_string() or "nenhum")
print("\nValores nulos por coluna (Query 2):")
print(q2.isna().sum()[lambda s: s > 0].to_string() or "nenhum")
print(f"\nFuncionários duplicados - Q1: {q1['employee_id'].duplicated().sum()} | "
      f"Q2: {q2['employee_id'].duplicated().sum()}")

sem_depto = q1[q1["department_name"].isna()]
print("\nFuncionário(s) sem departamento (mantidos pelo LEFT JOIN na Query 1):")
print(sem_depto[["employee_id", "first_name", "last_name", "job_title", "salary"]]
      .to_string(index=False))
print("-> Na Query 2 esse funcionário sai pelo filtro WHERE region_name IS NOT NULL,"
      " por isso ela tem 1 linha a menos.")

# Tratamento: identifica o departamento ausente em vez de apagar a linha
q1["department_name"] = q1["department_name"].fillna("Sem departamento")
# Tratamento: estado/província vazio (Londres) recebe um rótulo
q2["state_province"] = q2["state_province"].fillna("Não informado")

# ---------------------------------------------------------------------------
# 3. Estatística descritiva dos salários
# ---------------------------------------------------------------------------
titulo("3. ESTATÍSTICA DESCRITIVA - SALÁRIO")
sal = q1["salary"]
q1_, q3_ = sal.quantile(0.25), sal.quantile(0.75)
iqr = q3_ - q1_
lim_sup = q3_ + 1.5 * iqr
estat = {
    "Quantidade": len(sal),
    "Média": sal.mean(),
    "Mediana": sal.median(),
    "Mínimo": sal.min(),
    "Máximo": sal.max(),
    "Desvio padrão": sal.std(),
    "1º quartil (Q1)": q1_,
    "3º quartil (Q3)": q3_,
    "Amplitude interquartil (IQR)": iqr,
    "Limite superior (Q3 + 1,5*IQR)": lim_sup,
}
for nome, valor in estat.items():
    print(f"{nome:<32} {valor:>12,.2f}" if nome != "Quantidade" else f"{nome:<32} {valor:>12}")

outliers = q1[q1["salary"] > lim_sup].sort_values("salary", ascending=False)
print(f"\nOutliers (salário > {moeda(lim_sup)}): {len(outliers)} funcionário(s)")
print(outliers[["first_name", "last_name", "department_name", "job_title", "salary"]]
      .to_string(index=False))

# ---------------------------------------------------------------------------
# 4. Salários por departamento
# ---------------------------------------------------------------------------
titulo("4. SALÁRIOS POR DEPARTAMENTO")
por_depto = (q1.groupby("department_name")["salary"]
             .agg(funcionarios="count", media="mean", mediana="median",
                  minimo="min", maximo="max", folha_total="sum")
             .sort_values("media", ascending=False))
print(por_depto.round(2).to_string())

# ---------------------------------------------------------------------------
# 5. Salários por cargo
# ---------------------------------------------------------------------------
titulo("5. SALÁRIOS POR CARGO")
por_cargo = (q1.groupby("job_title")["salary"]
             .agg(funcionarios="count", media="mean", minimo="min", maximo="max")
             .sort_values("media", ascending=False))
print(por_cargo.round(2).to_string())
print("\nTop 5 cargos com maior média salarial:")
print(por_cargo.head(5)["media"].round(2).to_string())
print("\n5 cargos com menor média salarial:")
print(por_cargo.tail(5)["media"].round(2).to_string())

# Posição do salário dentro da faixa oficial do cargo (MIN_SALARY a MAX_SALARY)
q1["posicao_faixa_%"] = ((q1["salary"] - q1["min_salary"])
                         / (q1["max_salary"] - q1["min_salary"]) * 100)
print(f"\nEm média, os salários estão em {q1['posicao_faixa_%'].mean():.1f}% "
      "da faixa salarial do cargo (0% = mínimo, 100% = máximo).")
no_teto = q1[q1["salary"] >= q1["max_salary"]]
print(f"Funcionários no teto (ou acima) da faixa do cargo: {len(no_teto)}")
if not no_teto.empty:
    print(no_teto[["first_name", "last_name", "job_title", "salary", "max_salary"]]
          .to_string(index=False))

# ---------------------------------------------------------------------------
# 6. Distribuição geográfica
# ---------------------------------------------------------------------------
titulo("6. DISTRIBUIÇÃO DOS FUNCIONÁRIOS POR LOCALIDADE")
for coluna, rotulo in [("region_name", "Região"), ("country_name", "País"), ("city", "Cidade")]:
    contagem = q2[coluna].value_counts()
    pct = (contagem / len(q2) * 100).round(1)
    print(f"\nFuncionários por {rotulo}:")
    print(pd.DataFrame({"funcionarios": contagem, "%": pct}).to_string())

# Junta as duas consultas para ver salário por região/cidade
geo = q2.merge(q1[["employee_id", "salary"]], on="employee_id", how="left")
print("\nSalário médio por cidade:")
print(geo.groupby("city")["salary"].agg(["count", "mean", "median"]).round(2)
      .sort_values("mean", ascending=False).to_string())

# ---------------------------------------------------------------------------
# 7. Gráficos
# ---------------------------------------------------------------------------
titulo("7. GERANDO GRÁFICOS")

# 7.1 Histograma dos salários
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(sal, bins=12, color=COR, edgecolor="white")
ax.axvline(sal.mean(), color=COR_DESTAQUE, linestyle="--", linewidth=2,
           label=f"Média: {moeda(sal.mean())}")
ax.axvline(sal.median(), color="#333333", linestyle=":", linewidth=2,
           label=f"Mediana: {moeda(sal.median())}")
ax.set_title("Distribuição dos salários dos funcionários (n = 107)")
ax.set_xlabel("Salário (US$)")
ax.set_ylabel("Quantidade de funcionários")
ax.legend()
fig.tight_layout()
fig.savefig(IMAGENS / "01_histograma_salarios.png", dpi=120)
plt.close(fig)

# 7.2 Boxplot geral (mostra os outliers)
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.boxplot(sal, vert=False, widths=0.5, patch_artist=True,
           boxprops=dict(facecolor="#CFE0F5", color=COR),
           medianprops=dict(color=COR_DESTAQUE, linewidth=2),
           flierprops=dict(marker="o", markerfacecolor=COR_DESTAQUE, markersize=7))
ax.set_yticks([])
ax.set_title(f"Boxplot dos salários - {len(outliers)} outliers acima de {moeda(lim_sup)}")
ax.set_xlabel("Salário (US$)")
fig.tight_layout()
fig.savefig(IMAGENS / "02_boxplot_salarios.png", dpi=120)
plt.close(fig)

# 7.3 Boxplot por departamento
ordem = por_depto.index.tolist()
fig, ax = plt.subplots(figsize=(11, 6))
ax.boxplot([q1.loc[q1["department_name"] == d, "salary"] for d in ordem],
           vert=False, patch_artist=True,
           boxprops=dict(facecolor="#CFE0F5", color=COR),
           medianprops=dict(color=COR_DESTAQUE, linewidth=2))
ax.set_yticks(range(1, len(ordem) + 1))
ax.set_yticklabels([f"{d} (n={por_depto.loc[d, 'funcionarios']})" for d in ordem])
ax.invert_yaxis()
ax.set_title("Salários por departamento (ordenado pela média)")
ax.set_xlabel("Salário (US$)")
fig.tight_layout()
fig.savefig(IMAGENS / "03_boxplot_por_departamento.png", dpi=120)
plt.close(fig)

# 7.4 Média salarial por departamento (barras)
fig, ax = plt.subplots(figsize=(10, 6))
medias = por_depto["media"].sort_values()
ax.barh(medias.index, medias.values, color=COR)
ax.axvline(sal.mean(), color=COR_DESTAQUE, linestyle="--", label="Média geral")
for i, v in enumerate(medias.values):
    ax.text(v + 150, i, f"{v:,.0f}".replace(",", "."), va="center", fontsize=9)
ax.set_title("Média salarial por departamento")
ax.set_xlabel("Salário médio (US$)")
ax.legend()
fig.tight_layout()
fig.savefig(IMAGENS / "04_media_salarial_departamento.png", dpi=120)
plt.close(fig)

# 7.5 Funcionários por cidade
fig, ax = plt.subplots(figsize=(9, 5))
cidades = q2["city"].value_counts().sort_values()
ax.barh(cidades.index, cidades.values, color=COR)
for i, v in enumerate(cidades.values):
    ax.text(v + 0.5, i, str(v), va="center", fontsize=9)
ax.set_title("Quantidade de funcionários por cidade (n = 106)")
ax.set_xlabel("Funcionários")
fig.tight_layout()
fig.savefig(IMAGENS / "05_funcionarios_por_cidade.png", dpi=120)
plt.close(fig)

for arq in sorted(IMAGENS.glob("*.png")):
    print(f"Gráfico salvo: {arq.relative_to(BASE)}")

titulo("FIM DA ANÁLISE")
