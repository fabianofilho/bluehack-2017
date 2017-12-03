import numpy as np
import random
#import math

import logging
logging.getLogger().setLevel(logging.DEBUG)
df_path = "E:\Projetos\BlueHack\data\DF_RNA_2.csv"
df_alive = "E:\Projetos\BlueHack\data\DF_RNA_ALIVE_2.csv"



#le arquivo completo => Retorna lista de linhas
def read_arq(arquivo):
	conteudo =""
	lista= []
	arq = open(arquivo , 'rt')
	conteudo = arq.readline()
	while conteudo != '':
		if(conteudo[-1] =='\n'):
			conteudo = conteudo[:-1].replace(",",".")
		lista.append(conteudo)
		conteudo = arq.readline()
	arq.close()
	return lista


#Transforma dados lidos no csv em matriz
def arq_to_mat(lista,separator):
	i = 1
	tam = len(lista)
	result = []
	while(i < tam):
		aux = lista[i].split(separator) #linha -> [a,b,c,d]
		aux2 = []
		j =1
		while(j < len(aux)):
			#print(aux[j])
			try:
				aux2.append(float(aux[j]))
			except:
				pass
			j+=1

		result.append(aux2)

		i +=1
	return result


# Limpa colunas da lista
def clean_list(lista,to_remove):
	i = 1
	tam = len(lista)
	while(i < tam):
		lista[i][14] = lista[i][14]/1000.0
		lista[i][2] = lista[i][2]/10.0
		lista[i][10] = lista[i][10]/10.0
		aux = lista[i]+[]
		for rem in to_remove:
			lista[i].remove(aux[rem])
		i = i+1

	lista.remove(lista[0])
	return lista

# Recupera a coluna
def get_colum(lista, coluna):
	i = 1
	tam = len(lista)
	newList = []
	while(i < tam):
		newList.append([lista[i][coluna]])
		i = i+1

	return newList


# Retorna dois agrupamentos aleatorios
# result -> tamanho definido
# aux -> resto
def get_random_data(lista1,lista2,percentage):
	result = []
	result2 = []
	aux = lista1 + []
	aux2 = lista2 + []
	quant = int(len(lista1)*percentage)
	i = 0
	while(i< quant):
		res = random.randrange(0,len(aux))
		result.append(aux[res])
		result2.append(aux2[res])
		aux.remove(aux[res])
		aux2.remove(aux2[res])
		i+=1

	return {"l1":[result,aux],"l2":[result2,aux2]}


def sub_groups(lista1,lista2, tam):
	result1 = []
	result2 = []

	quant = int(len(lista1)/tam)


	i = 0
	j = 0
	if(tam ==1 ):
		result1.append(lista1)
		result2.append(lista2)

	elif(tam == len(lista1)):
		quant = tam
		while(j < quant):
			result1.append([lista1[j]])
			result2.append([lista2[j]])
			j+=1

	else:
		while(j < quant):
			result1.append(lista1[i:i+quant])
			result2.append(lista2[i:i+quant])
			i += tam
			j+=1

	return result1,result2





print("LENDO AQUIVO")
lines1 = read_arq(df_path)
lines1 = arq_to_mat(lines1,";")

lines2 = read_arq(df_alive)
lines2 = arq_to_mat(lines2,";")

print("ORGANIZANDO DADOS")
lines = lines1 + lines2

cleaned_list = clean_list(lines,[0])

labels = ([[0.0]] * len(lines1)) + ([[1.0]] * len(lines2))

result_randomization = get_random_data(lines,labels,0.8)

print("IMPORTANDO RNA")
import mxnet as mx

import pandas as pd 

train_data = pd.DataFrame(result_randomization["l1"][0]).values
train_label = pd.DataFrame(result_randomization["l2"][0]).values
	
# train_data = mx.nd.array(result_randomization["l1"][0])
# train_label = mx.nd.array(result_randomization["l2"][0])


#train_data = np.array(result_randomization["l1"][0])#np.array(cleaned_list)
#train_label = np.array(result_randomization["l2"][0])#np.array(wheight)

#train_data = np.array(lines)
#eval_label = np.array(labels)

eval_data = pd.DataFrame(result_randomization["l1"][1]).values
eval_label = pd.DataFrame(result_randomization["l2"][1]).values

# eval_data = mx.nd.array(result_randomization["l1"][1])
# eval_label = mx.nd.array(result_randomization["l2"][1])



#Importando libs

batch_size = 10

print("PREPARANDO REDE")
train_iter = mx.io.NDArrayIter(train_data,train_label, batch_size, shuffle=True,label_name='lin_reg_label')
eval_iter = mx.io.NDArrayIter(eval_data, eval_label, batch_size, shuffle=False)


## PURO TESTE

print("CRIANDO CAMADAS")
X = mx.sym.Variable('data')
Y = mx.symbol.Variable('lin_reg_label')

fully_connected_layer  = mx.sym.FullyConnected(data=X, name='fc1', num_hidden = 1)

#DEBUG
act1 = mx.sym.Activation(data = fully_connected_layer,name="ac1",act_type =	"relu")

fully_connected_layer_2 = mx.sym.FullyConnected(data=act1, name='fc2', num_hidden = 256)
act2 = mx.sym.Activation(data =	fully_connected_layer_2,name="ac2",act_type= "relu")

#fully_connected_layer_3 = mx.sym.FullyConnected(data=act2, name='fc3', num_hidden = 32)
#act3 = mx.sym.Activation(data =	fully_connected_layer_3,name="ac3",act_type= "relu")

#fully_connected_layer_4 = mx.sym.FullyConnected(data=act3, name='fc4', num_hidden = 16)
#act4 = mx.sym.Activation(data = fully_connected_layer_4,name="ac4",act_type= "relu")

#fully_connected_layer_x = mx.sym.FullyConnected(data=act4, name='fc5', num_hidden = 8)
#actx = mx.sym.Activation(data = fully_connected_layer_x,name="ac4",act_type= "relu")
actx = act2

fully_connected_layer_x = mx.sym.FullyConnected(data=actx, name='fc6', num_hidden = 1)
#actx = mx.sym.Activation(data = fully_connected_layer_x,name="ac4",act_type= "relu")


fully_connected_layer_r = fully_connected_layer_x

#fully_connected_layer_r = fully_connected_layer_4
#fully_connected_layer_r = act4
#fully_connected_layer_r = act3
#fully_connected_layer_r = act2


#fully_connected_layer_r = fully_connected_layer
print("DEFININDO REGRESSAO")
lro = mx.sym.LinearRegressionOutput(data=fully_connected_layer_r, label=Y, name="lro")

model = mx.mod.Module(
    symbol = lro ,
    data_names=['data'],
    label_names = ['lin_reg_label']# network structure
)

mx.viz.plot_network(symbol=lro)

#TREINANDO SAPORRA

print("TREINANDO")
model.fit(train_iter, eval_iter,
            optimizer_params={'learning_rate':0.005, 'momentum': 0.9},
            num_epoch=1,
            #eval_metric='mse',
            eval_metric='rmse',
            #batch_end_callback = mx.callback.Speedometer(1, 1))
            #batch_end_callback = mx.callback.Speedometer(batch_size, columns_size))
            batch_end_callback = mx.callback.Speedometer(1, 3))

print("PREDIZENDO")
model.predict(eval_iter).asnumpy()

metric = mx.metric.MSE()
b= model.score(eval_iter, metric)

print(b)
