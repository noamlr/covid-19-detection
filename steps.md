A DECOVNET recebe como input duas coisas:
 - CT original no formato .npy (array 3D)
 - Máscara binária da segmentação do pulmão (pode ser treinada com a 2dunet, mas eu não vi pesos disso daqui, então uso nossas máscaras binárias e converto elas para o .npy 3D)

Nota:
Executamos a parte da rede da 2dunet só para converter as CTs no formato correto

## STEPS:
1. Ir na pasta "preprocess/preprocess-obtain-puredicom" e criar o "patients.csv" de conversão dos dicoms para o formato de input da 2dunet. O csv tem que ter o seguinte formato:

```
path_in,name
/ssd/share/CT-Original/DICOM-HCPA/exame-pulmao/NEG-001,NEG-001
/ssd/share/CT-Original/DICOM-HMV/exame-pulmao/C123/TEB0IYOF/Q34XOCAJ,C123
...
```
(Deixei o patients\_dicom.csv que tem os dados do HMV+HCPA com as pastas certas e um nome, e para o SPGC o arquivo é patients-spgc.csv)

Esse nome tem que estar na linha 86 do arquivo main.py:
```
linha 86: df = pd.read_csv('patients-spgc-test.csv') # mudar pelo nome do arquivo
```

2. Executar o main.py -> vai criar uma pasta "./normal" e adicionar ali o formato .npy de entrada para a "2dunet"

3. Cópiar todos os "preprocess/preprocess-obtain-puredicom/normal/\*.npy" para "2dunet/NCOV-BF/NpyData"

4. Ir para "2dunet/NCOV-BF/ImageSets" and edit lung\_test.txt só com os nomes dos arquivos em "preprocess/preprocess-obtain-puredicom/normal/" sem o .npy como no exemplos dos arquivos lung\_test\_hmvhcpa.txt ou spgc (pode usar o mesmos caso esteja trabalhando com o mesmo dataset)

5. Ir para 2dunet e executar:
```
CUDA_VISIBLE_DEVICES=0 python test.py cfgs/test.yaml
```
Na pasta "unet-results" vai ter os seguintes formatos:
```
cap020-dlmask.npy  cap020.npy
```

6. Copy all patients.npy from "2dunet/unet-results" to "deCoVnet/NCOV-BF/NpyData-dlmask" (é dizer cópiar só os formatos tipo cap020.npy e não os cap020-dlmask.npy)


### STEPS DO PHNN
Aqui precisa fazer seu proceso para obter da sua segmentação formato .npy. Neste caso, a máscara binária é de 0 para o background e 1 para o pulmão (verificar bem as dimensões e direção dos eixos de saída, tem que ser os mesmo que os .npy do paso 6.)

7. Na pasta "preprocess/phnn2decovnet" criar o arquivo patients.csv com o seguinte formato:
```
path_in,path_out
/ssd/share/SPGC-SEGMENTED/Cap subjects/crop\_by\_mask\_cap020.nii.gz,/home/users/nmlromero/other-methods/sydney0zq/covid-19-detection/deCoVnet/NCOV-BF/NpyData-dlmask/cap020-dlmask.npy
/ssd/share/SPGC-SEGMENTED/Cap subjects/crop\_by\_mask\_cap026.nii.gz,/home/users/nmlromero/other-methods/sydney0zq/covid-19-detection/deCoVnet/NCOV-BF/NpyData-dlmask/cap026-dlmask.npy
```
path\_in: Máscara segmentada pelo abordagem PHNN
path\_out: Path para salvar a segmentação no formato .npy (deixar com o -dlmask.npy, formato de nome do step 6)

O PHNN não tinha a mesma direção nos eixos nem escalas, eu mudei um pouco o código por isso, mas talvez sua abordagem nem precise

8. Se usar outro nome do arquivo, mudar no utils.py o csv a ler e após executar:
```
python utils.py 
```
criar a pasta "deCoVnet/NCOV-BF/NpyData-dlmask" se ela não existir

Se o path\_out não está na "deCovnet/NCOV-BF/NpyData-dlmask/", cópiar os -dlmask.npy gerados para lá

#### Fim dos steps para o PHNN

9. Tem que ter os arquivos XYZ.npy e XYZ-dlmask.npy no "deCovnet/NCOV-BF/NpyData-dlmask". Na pasta " deCoVnet/NCOV-BF/ImageSets" criar o arquivo all\_exams.txt com os nomes dos arquivos .npy (sem o -dlmask.npy ou o .npy) correspondentes da pasta "deCoVnet/NCOV-BF/NpyData-dlmask" (tem um exemplo no all\_exams.txt)

10. Na pasta deCoVnet executar:
```
python cropresize.py 
```

A pasta "deCoVnet/NCOV-BF/NpyData-clip-size224x336" vai ser criada com os .npy e -dlmask.npy que são a entrada da rede deCoVnet

11. Nas pastas "deCoVnet/NCOV-BF/ImageSets/foldN" tem os arquivos de split treino/validação ncov... é para classe COVID, normal... para classe Não covid (acho que do fold 1 até o 5 é do split certo para os treinos de HMV-HCPA) e no fold6 (só para facilitar deixei o ternario para a SPGC)

12. Tem que rodar fold por fold o treino: (os parâmtros no cfgs/trainval.yaml INIT\_MODEL\_PATH: "" e RESUME\_EPOCH: 0)
```	
python train.py cfgs/trainval.yaml 1    # trainternary.py para 3 classes, e mudar no trainval.yaml o NUM_CLASSES: 3
python train.py cfgs/trainval.yaml 2
python train.py cfgs/trainval.yaml 3
python train.py cfgs/trainval.yaml 4
python train.py cfgs/trainval.yaml 5
```
	
Caso o treino parar numa época pode voltar a retomar executando o mesmo comando mudando na cfgs/trainval.yaml a época que deixou e o modelo inicial nos parâmetros: INIT_MODEL_PATH e RESUME_EPOCH

13. Para rodar os testes, colocar no arquivo cfgs/test.yaml o path da época escolhida e rodar para cada fold (parâmetro PRETRAINED\_MODEL\_PATH no test.yaml)
```
python test.py cfgs/test.yaml 1    # testternary.py para 3 classes e mudar no test.yaml o NUM_CLASSES: 3
```

### NOTA: Eu fiz quase todas as CTs com paths absolutos, cuidado se tentar usar elas mesmas
