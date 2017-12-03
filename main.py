#
# Blue Hack
#
# João Carlos Pandolfi Santana - 2017
#
###################################################

# Importing libs
import pandas as pd
import numpy as np


# Variables
dn_csv_file = "E:\Projetos\BlueHack\data\CSV\DNPR2008_2016.csv"
do_csv_file = "E:\Projetos\BlueHack\data\CSV\DOPR2008_2016.csv"

sih2008_csv_file = "E:\Projetos\BlueHack\data\CSV\SIHPR2008.csv"

csv_df_merge = "E:\Projetos\BlueHack\data\DF_MERGE.csv"
csv_df_prepared = "E:\Projetos\BlueHack\data\DF_PREPARED.csv"
csv_df_rna = "E:\Projetos\BlueHack\data\DF_RNA.csv"
csv_df_rna_alive = "E:\Projetos\BlueHack\data\DF_RNA_ALIVE.csv"
csv_df_integrated = "E:\Projetos\BlueHack\data\DF_INTEGRATED.csv"

def findColumn(df,data_key):
	return df[data_key][df[data_key].notnull()]

def findColumn2(df,data_key):
	return df[data_key]

def filterByType(df,data_type):
	return df[df == data_type]

def filterMaxWith(df,data_type):
	return df[df >= data_type]

def filterMinWith(df,data_type):
	return df[df <= data_type]

def findListInDfColumn(df,column,p_list):
	return df[df[column].isin(p_list)]

def findListInDf(df,p_list):
	return df[df.isin(p_list)]


# Reading data

df_dn = pd.read_csv(dn_csv_file)
df_do = pd.read_csv(do_csv_file)
df_sih2008 = pd.read_csv(sih2008_csv_file)

#df_merge = df_dn.merge(df_do, left_on='NUMERODN', right_on='NUMERODN', how='outer')
#df_merge = pd.concat([df_dn, df_do], axis=1, join='inner')
#df_merge = df_dn.set_index('NUMERODN').join(df_do.set_index('NUMERODN'), on='NUMERODN')
#df_merge = df_dn.set_index('NUMERODN').join(df_dn.set_index('NUMERODN'),lsuffix='_dn', rsuffix='_do',how="outer")

# Integrating data
col_dn = df_do[df_do["NUMERODN"].notnull()]["NUMERODN"]
df_in_dn_do = df_dn[df_dn["NUMERODN"].isin(col_dn)]
df_in_do_dn = df_do[df_do["NUMERODN"].isin(col_dn)]

df_merge = df_in_dn_do.set_index('NUMERODN').join(df_in_do_dn.set_index('NUMERODN'),lsuffix='_dn', rsuffix='_do')

#df_merge = pd.read_csv(csv_df_merge)




# ---- LIMPANDO BASE --> DEIXANDO SO OS CURIOSOS

# -- LIMPAR BEBE QUE TEVE CIRURGIA
df_merge = df_merge[df_merge["CIRURGIA"] != 1]

# -- LIMPAR BEBE QUE NAO TEVE ASSIT MEDICA
df_merge = df_merge[df_merge["ASSISTMED"] != 2]

# -- LIMPAR BEBE QUE NAO TEVE EXAME
df_merge = df_merge[df_merge["EXAME"] != 2]



# --

def normalize_data(df_merge):
	# -- APGAR

	# depois de 5 min
	apgar5 = findColumn(df_merge,"APGAR5")
	apgar5_ruim = filterMinWith(apgar5,3.0)
	apgar5_moderado = filterMinWith(apgar5,6.0) - apgar5_ruim # 4 a 6
	apgar5_bom = filterMaxWith(apgar5,7.0) # 7 a 10 

	# primeiro minuto
	apgar1 = findColumn(df_merge,"APGAR1")
	apgar1_ruim = filterMinWith(apgar1,3.0)
	apgar1_moderado = filterMinWith(apgar1,6.0) - apgar1_ruim # 4 a 6
	apgar1_bom = filterMaxWith(apgar1,7.0) # 7 a 10 

	delta_apgar = apgar1 - apgar5 # NEGATIVO A CRIANCA PIOROU
	soma_apgar = apgar1 + apgar5 # SOMA DOS APGAR

	const_apgar_soma_bom = 14 # 7 bom1 + 7 bom5
	const_baixo_peso = 2500

	baixo_soma_apgar = soma_apgar[soma_apgar < const_apgar_soma_bom]

	peso_apgar_soma_ruim = df_merge[df_merge.index.isin(baixo_soma_apgar.index)]["PESO_dn"]

	test2 = filterMinWith(peso_apgar_soma_ruim,const_baixo_peso)

	# APGAR BAIXO ESTA RELACIONADO COM PESO BAIXO !

	piora_apgar = delta_apgar[delta_apgar < 0]

	peso_apgar_delta = df_merge[df_merge.index.isin(piora_apgar.index)]["PESO_dn"]

	test2 = filterMinWith(peso_apgar_delta,const_baixo_peso)

	# ----------------- FISGA DE TESTE SAO BEBES COM PESO BAIXO ------- 


	# VARIAVEIS PARA RNA
	df_merge["delta_apgar"] = (df_merge["APGAR1"] - df_merge["APGAR5"])
	df_merge["piora_apgar"] = (df_merge["APGAR1"] - df_merge["APGAR5"]) < 0
	df_merge["soma_apgar"] = df_merge["APGAR1"] + df_merge["APGAR5"]
	df_merge["baixo_peso"] = df_merge["PESO_dn"] < const_baixo_peso

	df_merge["parto_induzido_norm"] = df_merge["STTRABPART"] == 1
	df_merge["sct_part_norm"] = df_merge["STCESPARTO"] == 1


	df_merge["mes_prenat_norm"] = 0 - df_merge["MESPRENAT"]
	# CONSULTAS
	# QTDGESTANT
	# IDADEMAE
	# TPAPRESENT
	# TPNASCASSI
	# LOCNASC

	# CAUSABAS --> LABEL

	# NORMALIZACAO 
	t_tam = df_merge["MESPRENAT"].shape
	t_count = 0
	for i, row in df_merge["MESPRENAT"].iteritems():
		print(t_count,t_tam)
		t_count +=1
		if(row <= 9):
			df_merge["mes_prenat_norm"][i] = 9 - row
		else:
			df_merge["mes_prenat_norm"][i] = 0


	df_merge["anomalia_cong"] = df_merge["IDANOMAL"] == 1


	df_merge.fillna(0, inplace=True)

	return df_merge


df_merge = normalize_data(df_merge)

df_merge.to_csv(csv_df_merge)

# --- Preparando DF para RNA

df_rna = pd.DataFrame()

df_rna["delta_apgar"] = df_merge["delta_apgar"]
df_rna["piora_apgar"] = df_merge["piora_apgar"]
df_rna["soma_apgar"] = df_merge["soma_apgar"]
df_rna["baixo_peso"] = df_merge["baixo_peso"]
df_rna["parto_induzido_norm"] = df_merge["parto_induzido_norm"]
df_rna["sct_part_norm"] = df_merge["sct_part_norm"]
df_rna["mes_prenat_norm"] = df_merge["mes_prenat_norm"]
df_rna["anomalia_cong"] = df_merge["anomalia_cong"]

# VARIAVEIS SABIDAMENTE IMPORTANTES
df_rna["CONSULTAS"] = df_merge["CONSULTAS"]
df_rna["QTDGESTANT"] = df_merge["QTDGESTANT"]
df_rna["IDADEMAE"] = df_merge["IDADEMAE_dn"]
df_rna["TPAPRESENT"] = df_merge["TPAPRESENT"]
df_rna["TPNASCASSI"] = df_merge["TPNASCASSI"]
df_rna["LOCNASC"] = df_merge["LOCNASC"]
df_rna["PESO"] = df_merge["PESO_dn"]
df_rna["ESCMAE"] = df_merge["ESCMAE_dn"]
df_rna["ESTCIVMAE"] = df_merge["ESTCIVMAE"]
df_rna["SEXO"] = df_merge["SEXO_dn"]
df_rna["GESTACAO"] = df_merge["GESTACAO_dn"]
df_rna["RACACOR"] = df_merge["RACACOR_dn"]

df_rna.to_csv(csv_df_rna)


# --- Preparando DF vivos para RNA

df_dn2 = df_dn[~df_dn["NUMERODN"].isin(col_dn)]
df_dn2 = df_dn2[0: 14000]

df_dn2["PESO_dn"] = df_dn2["PESO"]

df_dn2 = normalize_data(df_dn2)
df_dn2.to_csv(csv_df_prepared)


df_rna_vivo = pd.DataFrame()

df_rna_vivo["delta_apgar"] = df_dn2["delta_apgar"]
df_rna_vivo["piora_apgar"] = df_dn2["piora_apgar"]
df_rna_vivo["soma_apgar"] = df_dn2["soma_apgar"]
df_rna_vivo["baixo_peso"] = df_dn2["baixo_peso"]
df_rna_vivo["parto_induzido_norm"] = df_dn2["parto_induzido_norm"]
df_rna_vivo["sct_part_norm"] = df_dn2["sct_part_norm"]
df_rna_vivo["mes_prenat_norm"] = df_dn2["mes_prenat_norm"]
df_rna_vivo["anomalia_cong"] = df_dn2["anomalia_cong"]

df_rna_vivo["CONSULTAS"] = df_dn2["CONSULTAS"]
df_rna_vivo["QTDGESTANT"] = df_dn2["QTDGESTANT"]
df_rna_vivo["IDADEMAE"] = df_dn2["IDADEMAE"]
df_rna_vivo["TPAPRESENT"] = df_dn2["TPAPRESENT"]
df_rna_vivo["TPNASCASSI"] = df_dn2["TPNASCASSI"]
df_rna_vivo["LOCNASC"] = df_dn2["LOCNASC"]
df_rna_vivo["PESO"] = df_dn2["PESO"]
df_rna_vivo["ESCMAE"] = df_dn2["ESCMAE"]
df_rna_vivo["ESTCIVMAE"] = df_dn2["ESTCIVMAE"]
df_rna_vivo["SEXO"] = df_dn2["SEXO"]
df_rna_vivo["GESTACAO"] = df_dn2["GESTACAO"]
df_rna_vivo["RACACOR"] = df_dn2["RACACOR"]

df_rna_vivo.to_csv(csv_df_rna_alive)

# ----------------------------------------------------------------------------------------------------------
'''
# ------------------ TESTES ----------------------------
# Searching data
ds_evento = findColumn(df_merge,"DSEVENTO")
ds_explicia = findColumn(df_merge,"DSEXPLICA")
causabas = findColumn(df_merge,"CAUSABAS")
causabas_o = findColumn(df_merge,"CAUSABAS_O")
causabas_r = findColumn(df_merge,"CAUSABAS_R")
compara_cb = findColumn(df_merge,"COMPARA_CB")
atestado = findColumn(df_merge,"ATESTADO")
circobito = findColumn(df_merge,"CIRCOBITO") # 1 - acidente | 2 - suicidio | 3 - homicidio | 4 - outros | 9 - ignorado

print("Todo obito nao teve reselecao?")
print(causabas_r.size == 0 and compara_cb.size == 0)

print("Ninguem morreu por culpa da mae?")
print(findColumn(df_merge,"CAUSAMAT").size == 0)

# Tipo de obito no parto
obito_parto = findColumn(df_merge,"OBITOPARTO")
obito_parto_du = filterByType(obito_parto, 2.0)
obito_parto_de = filterByType(obito_parto, 3.0)
obito_parto_ig = filterByType(obito_parto, 9.0)
obito_parto_ant = filterByType(obito_parto, 1.0)

# Peso baixo
peso = findColumn(df_merge,"PESO_do")
peso_baixo = filterMinWith(peso,1000)

# Diferenca peso
diferenca_peso = df_merge[df_merge["PESO_do"] != df_merge["PESO_dn"]]["PESO_dn"] - df_merge[df_merge["PESO_do"] != df_merge["PESO_dn"]]["PESO_do"]


# Semanas de gestacao
dt_seman_gest = findColumn(df_merge,"GESTACAO_do")
seman_gest = {}
seman_gest["ate22"] = filterByType(dt_seman_gest,1.0)
seman_gest["22a27"] = filterByType(dt_seman_gest,2.0)
seman_gest["28a31"] = filterByType(dt_seman_gest,3.0)
seman_gest["32a36"] = filterByType(dt_seman_gest,4.0)
seman_gest["37a41"] = filterByType(dt_seman_gest,5.0)
seman_gest["42mais"] = filterByType(dt_seman_gest,6.0)

dt_seman_gest2 = findColumn(df_merge,"GESTACAO")



# Semana da gestacao que deu problema


# Numero de consutas da mae
consprenat = findColumn(df_merge,"CONSPRENAT")

#Consultas
consultas = findColumn(df_merge,"CONSULTAS")
consulta = {}
consulta["nenhuma"] = filterByType(consultas,1.0)
consulta["1a3"] = filterByType(consultas,2.0)
consulta["4a6"] = filterByType(consultas,3.0)
consulta["4a7"] = filterByType(consultas,4.0)
consulta["ignorado"] = filterByType(consultas,9.0)

# -- Quem fez o parto
dt_prof_sala_parto = findColumn(df_merge,"TPNASCASSI") 
prof_sala_parto= {}
prof_sala_parto["medico"] = filterByType(dt_prof_sala_parto, 1.0) 
prof_sala_parto["enfermeira"] = filterByType(dt_prof_sala_parto, 2.0)
prof_sala_parto["parteira"]	= filterByType(dt_prof_sala_parto, 3.0)
prof_sala_parto["outros"] = filterByType(dt_prof_sala_parto, 4.0)
prof_sala_parto["ignorado"] = filterByType(dt_prof_sala_parto, 9.0)


# -- Qtd sala parto
assist_med = findColumn(df_merge,"ASSISTMED_do") 
assist_med_s = filterByType(assist_med,1.0)
assist_med_n = filterByType(assist_med,2.0)
assist_med_i = filterByType(assist_med,9.0)




# --> CALCULAR MES DE PRENATAL (atual - 9) ["MESPRENAT"]



#parto_induzido = df_merge[df_merge["STTRABPART"] == 1]

# ---

# -------------------------------------
tppos = findColumn(df_merge,"TPPOS_do")
idade = findColumn(df_merge,"IDADE_do")


#Filtering circobito
circobito_outros = filterByType(circobito,4.0)
circobito_ignorado = filterByType(circobito,9.0)

tppos_y = filterByType(tppos,"S")
tppos_n = filterByType(tppos,"N")

mais2ano = filterMaxWith(idade,700)
menos1ano = filterMinWith(idade,364)
print("Todos sao menores de 2 anos?")
mais2ano.size == 0


# Ver todos que nao investigou se tem causa base
tppos_with_causabas = causabas_o[causabas_o.index.isin(tppos_n.index)]

print("Todos que nao tiveram investigacao de morte, tiveram causa base?")
tppos_with_causabas.size == tppos_n.size

# ---- SABEMOS ----
# Todos que nao tiveram investigacao de morte, tiveram uma causa base
# -----------------




# ------ BUSCANDO A CAUSA DE MORTE -----
# Variaveis ()
linhaa_o = findColumn(df_merge,"LINHAA_O_do")
linhab_o = findColumn(df_merge,"LINHAB_O_do")
linhac_o = findColumn(df_merge,"LINHAC_O_do")
linhad_o = findColumn(df_merge,"LINHAD_O_do")
'''



# ---------------------------- INTEGRACAO COM SIH -------------------------------
# -- Tentativa de cruzar DN e DO com SIH
dt_dn_nasc_mae = findColumn(df_merge,"DTNASCMAE")
dt_dn_cep_res = findColumn(df_merge,"CEPRES_dn")

dt_sih_nasc = findColumn(df_sih2008,"NASC")
dt_sih_cep = findColumn(df_sih2008,"CEP")

# --------- NORMALIZANDO NASCIMENTO --------

dt_dn_nasc_mae_norm = []
dt_sih_nasc_norm = []
dt_aux = []

for i, row in dt_dn_nasc_mae.iteritems():
    aux = row
    day = int(aux // 1000000)
    aux -= day*1000000
    month = int(aux // 10000)
    year = int(aux - (month * 10000))
    dt_dn_nasc_mae_norm.append(str(day)+"/"+str(month)+"/"+str(year))  
    dt_aux.append(i)

d = {'date':dt_dn_nasc_mae_norm, 'id': dt_aux }
dt_dn_nasc_mae_norm = pd.DataFrame(data=d)
dt_aux = []

for i, row in dt_sih_nasc.iteritems():
	aux = row
	year = int(aux // 10000)
	aux -= year*10000
	month = int(aux//100)
	day = int(aux - (month*100))
	dt_sih_nasc_norm.append(str(day)+"/"+str(month)+"/"+str(year))  
	dt_aux.append(i)

d = {'date':dt_sih_nasc_norm, 'id': dt_aux }
dt_sih_nasc_norm = pd.DataFrame(data=d)

# ----------------------

# --- Cruzando dados ---
#dt_sih_with_dn = filterByType(dt_sih_nasc_norm["date"],dt_dn_nasc_mae_norm["date"][1]) #findListInDfColumn(dt_sih_nasc_norm,"date",dt_dn_nasc_mae_norm["date"])

filtered_by_cep_dtnasc = pd.DataFrame([],columns=df_sih2008.columns)

t_tam = dt_dn_nasc_mae_norm["date"].size
t_cont = 0
for k, row1 in dt_dn_nasc_mae_norm["date"].iteritems():
	dt_sih_with_dn = filterByType(dt_sih_nasc_norm["date"],row1)
	print(t_cont,t_tam)
	t_cont +=1
	#cada id do dt e um id do -> dt_sih_nasc e dt_sih_cep
	for m, row2 in dt_sih_with_dn.iteritems():
		filtered_by_cep_dtnasc.append(df_sih2008[df_sih2008["NASC"] == dt_sih_nasc[m]][df_sih2008["CEP"] == dt_sih_cep[m]])



csv_df_integrated = "E:\Projetos\BlueHack\data\DF_INTEGRATED.csv"
filtered_by_cep_dtnasc.to_csv(csv_df_integrated)

# ----------------------------------------- FIM INTEGRACAO --------------------------------------

# -------- ANALISES ----------- 
'''
sid_ranking = causabas_o.value_counts()
max_sid = sid_ranking[0]

# ----- O cara que teve peso baixo, morreu pq?
criancas_peso_baixo = df_in_do_dn[df_in_do_dn.index.isin(peso_baixo.index)]

causa_morte_crianca_peso_baixo = criancas_peso_baixo["CAUSABAS"]

sid_ranking_cpb = causa_morte_crianca_peso_baixo.value_counts()

# ----- Nos nascidos, quantos tem peso baixo?
cnas_peso = findColumn(df_dn,"PESO")
cnas_peso_baixo = filterMinWith(cnas_peso,1000)


# ----- Das criancas que morreram, quantas consultas fizeram?
criancas_peso_baixo_dn = df_in_dn_do[df_in_dn_do.index.isin(peso_baixo.index)]
consultas_cpb  = criancas_peso_baixo_dn["CONSULTAS"]

consulta_cpb = {}
consulta_cpb["nenhuma"] = filterByType(consultas_cpb,1.0)
consulta_cpb["1a3"] = filterByType(consultas_cpb,2.0)
consulta_cpb["4a6"] = filterByType(consultas_cpb,3.0)
consulta_cpb["4a7"] = filterByType(consultas_cpb,4.0)
consulta_cpb["ignorado"] = filterByType(consultas_cpb,9.0)


# ----------------------------------------------------------------------------------------------

'''


