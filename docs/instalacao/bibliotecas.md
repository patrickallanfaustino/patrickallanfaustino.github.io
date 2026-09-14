# Bibliotecas

## :simple-python: Instalando MINICONDA e PyTorch

O Miniconda é um importante pacote de bibliotecas Python voltados para o uso científico.
```bash
cd ~/Downloads
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
conda config --set auto_activate_base false

conda info
```

Para desativar o carregamento automatico, utilize `conda config --set auto_activate_base false`.

!!! note "Extra:"

    Para atualizar o gerenciador de pacotes conda use `conda update conda`. Para atualizar as bibliotecas dentro do ambiente `conda update --all` e para uma limpeza `conda clean --all -y`.


!!! warning "Atenção!"

    Certifique de que a instalação será no diretório `$HOME/miniconda3` confirmando `yes` para todas as respostas. **NÃO UTILIZE `sudo`**.


Agora, vamos criar um ambiente virtual e instalar o Pytorch. No diretório `$HOME`, crie um ambiente `gromacs-nnpot`:
```bash
cd ~/software
sudo apt install python3-venv libjpeg-dev python3-dev python3-pip
python3 -m venv gromacs-nnpot
source ~/software/gromacs-nnpot/bin/activate
python3 -m pip install --upgrade setuptools pip wheel
pip3 install torch torchvision
```

Para testar:
```bash
python3 -c 'import torch' 2> /dev/null && echo 'Success' || echo 'Failure' # retorna Success
python3 -c "import torch; print(torch.cuda.is_available())"                # retorna True
python3 -c "import torch; print(torch.cuda.get_device_properties(0))"      # retorna informações GPU
python3 -c "import torch; x = torch.rand(5, 3); print(x)"                  # retorna matriz
python3 -c "import torch; print(torch.__version__)"                        # retorna a versão do Torch
```

---
## :lucide-toolbox: Instalando ferramentas para topologias

!!! note "Nota:"

    A adoção de ambientes isolados visa assegurar a manutenção e mitigar incompatibilidades entre bibliotecas.


### TOOLKIT
É uma caixa de ferramenta com bibliotecas utilizadas em bioinformatica.

```bash
conda create --name mdtoolkit python=3.12

conda activate mdtoolkit

conda install -c conda-forge \
rdkit openbabel py3dmol pillow \
numpy scipy pandas matplotlib plotly seaborn scikit-learn \
jupyterlab ipykernel ipympl watermark jupyterlab-language-pack-pt-BR tqdm pytest \
parmed panedr pyedr pymbar alchemlyb statsmodels numba networkx \
pdb2pqr propka biopython \
mdanalysis waterdynamics mdaencore mdtraj


conda config --append channels salilab
conda install -c salilab modeller
```

Para utilizar o openbabel:
```bash
obabel -ismi ethanol.smi -opdb -O ethanol.pdb --title ETHANOL --gen3d --minimize --sd --ff GAFF --log

obabel -:'CCO' -ogro -O ethanol.gro --title ETHANOL --gen3d --minimize --sd --ff GAFF --log

obabel -:"CC(=O)OC1=CC=CC=C1C(=O)O" -opdb -O aspirin.pdb --title ASPIRIN --gen3d --minimize --sd --ff GAFF --log

obabel ethanol.gro -O ethanol.mol2

obabel ethanol.gro -opdb -O ethanol.pdb
```

Temas para o jupyter notebook:
```bash
pip install theme-darcula
pip install jupyterlab-theme-solarized-dark
pip install jupyterlab-day
pip install jupyterlab-solarized-light-theme
```

### AmberTools
É uma coleção de programas gratuitos e de código aberto usados ​​para configurar, executar e analisar simulações moleculares. Para instalar:

```bash
cd $HOME
conda create --name acpype
conda activate acpype
conda install --channel conda-forge ambertools openbabel
```

Em conjunto com o AmberTools, o **ACPYPE** é um pacote em python para gerar topologias de moléculas. Para instalar e utilizar:

```bash
conda install -c conda-forge acpype
acpype --version

acpype -i ethanol.mol2 -c bcc -n 0 -a amber2 -o gmx    # exemplo de uso para uma molécula de etanol.
```

### CGenFF
É um servidor web para gerar topologias de moléculas para o campo de força CHARMM36. É possivel obter as topologias e coordenadas diretamente no formato para Gromacs ou obter o arquivo `.str` para posterior conversão em ambiente. É necessário obter a molécula de interesse no formato `.mol2`. (:lucide-triangle-alert: Verifique o suporte 32 bits das bibliotecas no sistema!)

```bash
conda create --name cgenff python=3.7
conda activate cgenff
conda install networkx=2.3 numpy

python cgenff_charmm2gmx_py3_nx2.py ETH ethanol.mol2 ethanol.str charmm36-jul2022.ff     # o campo de força deverá estar no mesmo diretório de trabalho.
```

!!! note "Nota:"

    Os arquivos cgenff_charmm2gmx_py3_nx2.py podem ser obtidos [aqui](../assets/instalacao/cgenff_charmm2gmx_py3_nx2.py).

### LigPargen
É uma biblioteca desenvolvida para gerar topologias de moléculas para o campo de força OPLS. Faça o download do software [BOSS](https://traken.chem.yale.edu/software.html), descompacte em um diretório de trabalho.

```bash
cd ~/software
sudo apt install csh
export BOSSdir=PATH_TO_BOSS_DIRECTORY            # pode ser incluido no arquivo ~/.bashrc
export PATH=$BOSSdir/scripts:$BOSSdir/exe:$PATH
```

Para criar o ambiente e instalar:

```bash
conda create --name ligpargen python=3.7
conda activate ligpargen
conda install -c conda-forge rdkit openbabel

cd ~/software
git clone https://github.com/Isra3l/ligpargen.git
pip install -e ligpargen
cd ligpargen
python -m unittest test_ligpargen/test_ligpargen.py
ligpargen -h
```

Para gerar topologia de moléculas, utilize:

```bash
ligpargen -s 'CCO' -n ethanol -p molecule -r ETH -c 0 -o 3 -cgen CM1A-LBCC -verbose -check

ligpargen -s CC(=O)[O-] -n ethanol -p molecule -r CAR -c -1 -o 3 -cgen CM1A -verbose -check
```

!!! warning "Atenção!"

    Recentemente o ligpargen tem apresentado problemas com a biblioteca RDKit. Se houver problemas com o teste:

    ```bash
    cd ~/software/ligpargen
    git checkout -b golden-local-rdkit-2022.09.1_1

    python -c "
    import os, ligpargen.tools.utilities as u, ligpargen.topology.Molecule as m
    wd = os.path.join(os.getcwd(),'test_ligpargen')
    mol,_,_,_ = u.generateRDkitMolecule(None,'c1ccccc1',wd,'MOL')
    open('test_ligpargen/goldenData/benzene_atoms.txt','w').write(
    '\n'.join(str(a) for a in m.fromRDkitMolecule(mol).atoms)+'\n')
    "

    python -m unittest test_ligpargen/test_ligpargen.py
    git commit -am "golden regenerado: rdkit 2022.09.1 py37h97e29ec_1 (diff de 1 ULP no dotProduct do Point3D)"
    ```

### Packmol
É uma biblioteca criada para construir configurações iniciais de sistemas complexos para simulação. Para instalar:

```bash
cd ~/software
python3 -m venv packmol
source $HOME/software/packmol/bin/activate
pip install packmol
```

---

## :lucide-toolbox: Instalando ferramentas para análises

!!! note

    A adoção de ambientes isolados visa assegurar a manutenção e mitigar incompatibilidades entre bibliotecas.


### Alchemlyb
É uma biblioteca voltado para análises de energia livres altamente eficiente, utilizando aprendizagem de máquina nas análises. Para instalar:

```bash
conda create -n mbar
conda activate mbar
conda install -c conda-forge alchemlyb pymbar jax jaxlib seaborn "jaxlib=*=*cuda*"
```

### MDAnalysis
É "agnóstica" quanto ao formato de arquivo (lê GROMACS, Amber, CHARMM, NAMD, etc. sem precisar converter). É orientada a objetos, permitindo seleções de átomos muito complexas e poderosas. É excelente para escrever ferramentas de análise personalizadas, embora possa ser ligeiramente mais lenta que o MDTraj em cálculos massivos.

```bash
conda create --name mdanalysis
conda activate mdanalysis
conda install -c conda-forge mdanalysis waterdynamics mdaencore
```

### MDTraj
Projetada para ser extremamente rápida e eficiente em memória, utiliza arrays do NumPy nativamente. É ideal para processar grandes volumes de dados (Big Data) e para converter formatos de trajetória. É frequentemente a escolha preferida para alimentar pipelines de Machine Learning devido à sua integração fácil com o ecossistema Scikit-learn/NumPy.

```bash
conda create --name mdtraj
conda activate mdtraj
conda install -c conda-forge mdtraj
```

### PyEMMA
Usada para analisar a cinética e a termodinâmica de sistemas moleculares. Ela pega dados de simulação (frequentemente processados via MDTraj) e ajuda a identificar estados metaestáveis, barreiras de energia e taxas de transição. É muito usada para entender folding de proteínas ou mudanças conformacionais complexas através de redução de dimensionalidade (TICA).

```bash
conda create --name pyemma
conda activate pyemma
conda install -c conda-forge pyemma
```

### ComplexMixture
É um pacote para estudar as interações entre soluto e solvente em misturas de moléculas com formas complexas.

!!! warning "Atenção!"

    Certifique-se de ter o Julia instalado.

```bash
cd ~/software/julia
julia -t auto
import Pkg; Pkg.activate(".")
import Pkg; Pkg.add(["ComplexMixtures", "PDBTools", "Plots", "EasyFit", "LaTeXStrings", "Packmol"])
```

---
## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
