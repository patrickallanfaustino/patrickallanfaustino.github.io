# Workflow de Instalação GROMACS 2026.x com CUDA 13.x

!!! info "Testado em"

    **Ubuntu 24.04.4** (kernel 6.17)

    - GROMACS: 2026.3
    - CUDA: 13.2

    **Ubuntu 26.04** (kernel 7.0)

    - GROMACS: 2026.3
    - CUDA: 13.2

## :lucide-laptop: Computador testado e pré-requisitos:
- Verificar minha [Workstation Home](../sobre.md).

Antes de começar, verifique se você atende aos seguintes requisitos:

- Máquina em Linux com distro Ubuntu com instalação limpa e atualizado.
- GPU série Ada Lovelace.
- Documentações [CUDA 13](https://docs.nvidia.com/cuda/index.html), [Drivers NVidia](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/introduction.html) e [GROMACS 2026.x](https://manual.gromacs.org/current/index.html).

Atualizar e instalar pacotes em sua máquina:
```bash
sudo apt update && sudo apt upgrade
sudo apt autoremove && sudo apt autoclean
sudo apt install \
    build-essential \
    libboost-all-dev \
    git \
    cmake \
    software-properties-common \
    ca-certificates \
    gpg \
    wget
```

Verifique a versão do kernel e bibliotecas:
```bash
uname -r
cat /etc/os-release
cmake --version
g++ --version
ldd --version
```

!!! tip

    Para instalar o Kernel GA (General Availability):
    ```bash
    sudo apt install linux-image-generic
    ```

    Para instalar o Kernel HWE (Hardware Enablement):
    ```bash
    sudo apt install --install-recommends linux-generic-hwe-24.04    # para Ubuntu 24.04
    sudo apt install --install-recommends linux-generic-hwe-26.04    # para Ubuntu 26.04
    ```

    Para remover kernel antigos incompatíveis:
    ```bash
    dpkg --list | egrep -i --color 'linux-image|linux-headers'
    ```

    Para compilar o CMake atual, utilize o repositório oficial do Kitware:
    ```bash
    cd ~/Downloads
    wget -O kitware-archive.sh https://apt.kitware.com/kitware-archive.sh
    sudo bash kitware-archive.sh
    sudo apt install cmake
    ```

Algumas configurações podem ajudar em sistemas dual boot:
```bash
# Instalar codecs, fontes e outros softwares
sudo apt install ubuntu-restricted-extras

# Conflitos de horários entre Windows e Ubuntu para casos de dualboot
timedatectl set-local-rtc 1 --adjust-system-clock

# Acesso ao disco NTFS do Windows
sudo apt install ntfs-3g
```

---
## :lucide-wrench: Instalando Timeshif
Software para criar snapshots do sistema e restaurar em caso de falhas. Para instalar:

=== "Ubuntu 24.04"

    ```bash
    sudo add-apt-repository ppa:teejee2008/timeshift
    sudo apt update
    sudo apt install timeshift
    ```

=== "Ubuntu 26.04"

    ```bash
    sudo apt update
    sudo apt install timeshift
    ```

!!! tip

    Se desejar, instale o [GRUB CUSTOMIZER](https://www.edivaldobrito.com.br/grub-customizer-no-ubuntu/) para gerenciar o inicializador e [MAINLINE](https://www.edivaldobrito.com.br/como-instalar-o-ubuntu-mainline-kernel-installer-no-ubuntu-e-derivados/) para gerenciar o kernel instalado.

    ```bash
    sudo add-apt-repository ppa:danielrichter2007/grub-customizer
    sudo apt update
    sudo apt install grub-customizer
    ```

    ```bash
    sudo add-apt-repository ppa:cappelikan/ppa
    sudo apt update
    sudo apt install mainline
    ```


---
## :lucide-search: Instalando CUDA 13.x

=== "Ubuntu 24.04"

    Verifique a compatibilidade da GPU antes. Para CUDA 12 ou superior, requer arquitetura Maxwell ou superior.
    ```bash
    lspci | grep -i nvidia
    ```

    Remova todos os driver relacionados que tiver instalado:
    ```bash
    sudo apt remove --autoremove --purge "*cuda*" "*cublas*" "*cufft*" "*cufile*" "*curand*" "*cusolver*" "*cusparse*" "*gds-tools*" "*npp*" "*nvjpeg*" "nsight*" "*nvvm*" "*nvidia*"
    ```
    ```bash
    sudo apt autoremove --purge
    ```

    Instale os pre-requisitos para CUDA:
    ```bash
    sudo apt update
    sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
    sudo apt install \
        g++ \
        freeglut3-dev \
        build-essential \
        ca-certificates \
        software-properties-common \
        dkms \
        curl \
        wget \
        libx11-dev \
        libxmu-dev \
        libxi-dev \
        libglu1-mesa-dev \
        libfreeimage-dev \
        libglfw3-dev
    ```

    Adicionar o repositório oficial NVIDIA CUDA:
    ```bash
    cd $HOME/Downloads
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    ```
    ```bash
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-archive-keyring.gpg
    sudo mv cuda-archive-keyring.gpg /usr/share/keyrings/cuda-archive-keyring.gpg
    ```
    ```bash
    echo "deb [signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/ /" | tee /etc/apt/sources.list.d/cuda-ubuntu2404-amd64.list
    ```
    ```bash
    sudo apt update
    ```

    Para avaliar as versões de drivers e CUDA disponíveis:
    ```bash
    apt search cuda-toolkit | grep -E "^cuda-toolkit"
    apt search cuda-drivers | grep -E "^cuda-drivers"
    apt search nvidia-driver | grep -E "^nvidia-driver-[0-9]+"
    ```

    Instalação:
    ```bash
    sudo apt install cuda-toolkit cuda-drivers libnccl2 libnccl-dev
    sudo apt install nvidia-gds
    ```

    Para configurar o compilador NVCC, edite o `~/.bashrc` e adicione:
    ```bash
    export CUDA_HOME=/usr/local/cuda
    export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
    export PATH=$CUDA_HOME/bin:$PATH
    ```
    ```bash
    source ~/.bashrc
    sudo dkms autoinstall
    reboot
    ```

    Para verificar a instalação, utilize:
    ```bash
    nvidia-smi
    nvcc --version
    ```

    !!! tip

        Para remover, utilize:

        ```bash
        sudo apt remove --purge "*cuda*" "*nvidia*" cuda-keyring
        sudo apt purge && sudo apt autoremove && sudo apt autoclean
        ```
        ```bash
        sudo rm -f /etc/apt/preferences.d/cuda-repository-pin-600
        sudo rm -f /etc/apt/sources.list.d/cuda*.list
        sudo rm -rf /var/cache/apt/*
        sudo apt clean all
        sudo apt update
        sudo reboot
        ```


=== "Ubuntu 26.04"

    !!! warning "Em construção"

        Conteúdo para Ubuntu 26.04 em breve.

---
## :lucide-gauge: Instalando LACT

O aplicativo [LACT](https://github.com/ilya-zlobintsev/LACT) é utilizado para controlar e realizar overclocking em GPU AMD, Intel e Nvidia em sistemas GNU/Linux.
```bash
cd $HOME/Downloads
wget https://github.com/ilya-zlobintsev/LACT/releases/download/v0.9.0/lact-0.9.0-0.amd64.ubuntu-2404.deb
sudo dpkg -i lact-0.9.0-0.amd64.ubuntu-2404.deb
sudo systemctl enable --now lactd
```

!!! warning

    Faça o download do pacote [LACT](https://github.com/ilya-zlobintsev/LACT/releases/) de acordo com a distribuição do Linux.


!!! note

    Para remover versões anteriores, utilize `sudo dpkg -r lact`.


---
## :lucide-thermometer: Instalando Hardware Sensors Indicator

O aplicativo [HSI](https://github.com/alexmurray/indicator-sensors) é utilizado para monitorar a temperatura de CPU, GPU, Motherboard, etc. Recomenda-se a instalação pela Central de Aplicativos [Snap](https://snapcraft.io/indicator-sensors) do Ubuntu e configurar para inicialização automatica com monitoramento da CPU (Tctl).
```bash
sudo snap install indicator-sensors

indicator-sensors
```

---
## :lucide-gem: Instalação do GROMACS 2026.x

**LIBTORCH** É possivel instalar a biblioteca [libtorch](https://pytorch.org/) para utilizar Redes Neurais. Verifique a versão mais recente. Utilize a pasta `Downloads`.
```bash
cd $HOME/Downloads
wget https://download.pytorch.org/libtorch/cu130/libtorch-shared-with-deps-2.10.0%2Bcu130.zip
unzip libtorch-shared-with-deps-2.10.0+cu130.zip
```

Podemos instalar algumas bibliotecas auxiliares para o GROMACS:
```bash
sudo apt install grace \
    hwloc \
    libhwloc-dev \
    libhdf5-dev \
    hdf5-tools \
    libhdf5-openmpi-dev \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    openmpi-bin \
    libopenmpi-dev \
    gfortran \
    libfftw3-dev \
    imagemagick \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    libxml2-dev \
    libtinyxml2-dev \
    libzstd-dev \
    zlib1g-dev \
    pkg-config
```

**PLUMED 2.x** Para instalar a biblioteca [Plumed](https://www.plumed.org/):
```bash
wget https://github.com/plumed/plumed2/releases/download/v2.10.1/plumed-src-2.10.1.tgz
tar -xzf plumed-src-2.10.1.tgz
cd plumed-2.10.1
./configure --prefix=$HOME/plumed --enable-mpi --enable-modules=all CXX=mpicxx CC=mpicc FC=mpifort
make -j$(nproc)
make install

plumed info --version
```

Atualize no `.bashrc`:
```bash
export PATH="$HOME/plumed/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/plumed/lib:$LD_LIBRARY_PATH"
export PLUMED_KERNEL="$HOME/plumed/lib/libplumedKernel.so"
```

=== "Ubuntu 24.04"

    A partir de agora, você poderá seguir a documentação oficial [guia de instalação](https://manual.gromacs.org/current/install-guide/index.html).
    ```bash
    cd $HOME/Downloads
    wget ftp://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz
    tar -xvf gromacs-2026.3.tar.gz && cd gromacs-2026.3
    sudo mkdir build && cd build
    ```

    Para compilar com Cmake (versão >=3.28):
    ```bash
    cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DGMX_OPENMP=ON \
    -DGMX_THREAD_MPI=ON \
    -DCMAKE_C_FLAGS="-O3 -march=native -mtune=native" \
    -DCMAKE_CXX_FLAGS="-O3 -march=native -mtune=native" \
    -DGMX_GPU=CUDA \
    -DGMX_GPU_FFT_LIBRARY=cuFFT \
    -DCUDAToolkit_ROOT=/usr/local/cuda \
    -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda \
    -DCMAKE_CUDA_ARCHITECTURES=native \
    -DCMAKE_INSTALL_PREFIX=$HOME/gromacs-cuda-torch \
    -DGMX_HWLOC=ON \
    -DGMX_USE_HDF5=ON \
    -DGMX_USE_PLUMED=ON \
    -DGMX_USE_COLVARS=INTERNAL \
    -DGMX_NNPOT=TORCH \
    -DGMX_EXTERNAL_TINYXML2=ON \
    -DGMX_EXTERNAL_ZLIB=ON \
    -DCMAKE_PREFIX_PATH="$HOME/Downloads/libtorch;/usr/local/cuda"
    ```

    Note que criei uma pasta chamada `gromacs-cuda-torch` para os arquivos compilados e indiquei com `-DCMAKE_INSTALL_PREFIX`, pois isso facilita a atualização do GROMACS no futuro.

    Agora é o momento de compilar, checar e instalar:
    ```bash
    make -j$(nproc)
    make check -j$(nproc)
    make install -j$(nproc)
    ```

=== "Ubuntu 26.04"

    !!! warning "Em construção"

        Conteúdo para Ubuntu 26.04 em breve.

Para carregar a biblioteca e invocar o GROMACS:
```bash
source $HOME/gromacs-cuda-torch/bin/GMXRC
gmx -version
```

!!! tip

    Você poderá editar o arquivo `$HOME/.bashrc` e adicionar o código `source $HOME/gromacs-cuda-torch/bin/GMXRC`. Assim, toda vez que abrir o terminal carregara o GROMACS.


---
## :simple-python: Instalando MINICONDA e PyTorch

O [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) é um importante pacote de bibliotecas Python voltados para o uso científico.
```bash
cd $HOME/Downloads
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
conda config --set auto_activate_base false
conda info
```

Com os comandos acima será carregado no prompt (`source ~/.bashrc`) o conda `base`. Para desativar o carregamento automatico, utilizar `conda config --set auto_activate_base false`.

!!! tip

    Para atualizar o gerenciador de pacotes conda use `conda update conda`. Para atualizar as bibliotecas dentro de um ambiente `conda update --all` e para uma limpeza `conda clean --all -y`.


!!! warning

    Certifique de que a instalação será no diretório `$HOME/miniconda3` confirmando `yes` para todas as respostas. **NÃO UTILIZE `sudo`**.


Agora, vamos criar um ambiente virtual e instalar o [Pytorch](https://pytorch.org/get-started/locally/). No diretório `$HOME`, crie um ambiente `gromacs-nnpot`:
```bash
cd $HOME
sudo apt install python3-venv libjpeg-dev python3-dev python3-pip
python3 -m venv gromacs-nnpot
source $HOME/gromacs-nnpot/bin/activate
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

!!! tip

    Caso deseje desistalar utilize `pip3 uninstall <biblioteca>`, para atualizar `pip3 install --upgrade <biblioteca>` e para listar os pacotes instalados `pip3 list`.


---

## :lucide-gem: Instalação do OpenMM 8.x

O [OpenMM](https://openmm.org/) é outro software baseado em Python para simulação de dinâmica molecular. Para sua instalação, vamos criar um ambiente virtual e instalar via pip no diretório padrão `$HOME`.
```bash
cd $HOME
python3 -m venv openmm
source $HOME/openmm/bin/activate
pip3 install openmm[cuda13]
```

Para sair do ambiente criado, basta utilizar `deactivate`. Para verificar a instalação, onde será realizado teste com a Referência, CPU, HIP e OpenCL:
```bash
python -m openmm.testInstallation
```

!!! note

    ***Extra:*** para compilar no Conda:
    ```bash
    conda create --name openmm
    conda activate openmm
    conda install -c conda-forge openmm openmmforcefields pdbfixer openmm-setup flask openmmtools pymbar
    ```


Para remover o ambiente conda criado `conda env remove --name openmm` e para listar todas os ambientes utilize `conda env list`.

---
## :lucide-dna: Instalando VMD e Pymol

O [VMD](https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=VMD) permite visualizar moléculas e realizar análises. Para instalação:
```bash
cd $HOME
wget https://www.ks.uiuc.edu/Research/vmd/alpha/vmd-2.0.1a1.bin.LINUXAMD64.tar.gz
tar xvzf vmd-2.0.1a1.bin.LINUXAMD64.tar.gz
cd  vmd-2.0.1a1
./configure
cd src
sudo make install -j$(nproc)
vmd
```

O [Pymol](https://www.pymol.org/) é outro software muito utilizado para visualização de moléculas:
```bash
conda create -n pymol python=3.10
conda activate pymol
conda install -c conda-forge pymol-open-source
```

---
## :lucide-calculator: Instalando o Julia

O [Julia](https://julialang.org/) é uma linguagem de programação voltada para cálculos científicos, similar ao Python. Para instalar:

```bash
cd $HOME
sudo apt install curl
curl -fsSL https://install.julialang.org | sh
```

Para atualizar, utilize no terminal `juliaup update`. Para remover utilize `juliaup self uninstall`.

---
## :lucide-toolbox: Instalando ferramentas para topologias: Toolkit, OpenBabel, AmberTools/ACPYPE, CGenFF, LigParGen e Packmol.

!!! note

    A adoção de ambientes isolados visa assegurar a manutenção e mitigar incompatibilidades entre bibliotecas.


**TOOLKIT**: é uma caixa de ferramenta com bibliotecas utilizadas em bioinformatica.

```bash
conda create --name mdtoolkit python=3.12

conda activate mdtoolkit

conda install -c conda-forge \
rdkit openbabel py3dmol pillow \
numpy scipy pandas matplotlib plotly seaborn scikit-learn \
jupyterlab ipykernel notebook nglview watermark jupyterlab-language-pack-pt-BR \
parmed panedr pyedr dssp pymbar alchemlyb statsmodels tqdm numba networkx ipympl pytest \
pdbfixer openmm pdb2pqr propka biopython requests netcdf4 pyjuliapkg

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

!!! note

    Para utilizar o notebook `jupyter lab`.


[AmberTools](https://ambermd.org/AmberTools.php) é uma coleção de programas gratuitos e de código aberto usados ​​para configurar, executar e analisar simulações moleculares.. Para instalar:

```bash
cd $HOME
conda create --name acpype
conda activate acpype
conda install --channel conda-forge ambertools openbabel
```

Em conjunto com o AmberTools, o [ACPYPE](https://github.com/alanwilter/acpype) é um pacote em python para gerar topologias de moléculas. Para instalar e utilizar:

```bash
conda install -c conda-forge acpype
acpype --version

acpype -i ethanol.mol2               # exemplo de uso para uma molécula de etanol.
```

[CGenFF](https://cgenff.com/) é um servidor web para gerar topologias de moléculas para o campo de força CHARMM36. É possivel obter as topologias e coordenadas diretamente no formato para Gromacs ou obter o arquivo `.str` para posterior conversão em ambiente. É necessário obter a molécula de interesse no formato `.mol2`. (:lucide-triangle-alert: Verifique o suporte 32bits das bibliotecas do sistema!)

```bash
conda create --name cgenff python=3.7
conda activate cgenff
conda install networkx=2.3 numpy

python cgenff_charmm2gmx_py3_nx2.py ETH ethanol.mol2 ethanol.str charmm36-jul2022.ff     # o campo de força deverá estar no mesmo diretório de trabalho.
```

[LigPargen](https://github.com/Isra3l/ligpargen/tree/main) é uma biblioteca desenvolvida para gerar topologias de moléculas para o campo de força OPLS. Faça o download do software [BOSS](https://traken.chem.yale.edu/software.html), descompacte em um diretório de trabalho.

```bash
sudo apt install csh
export BOSSdir=PATH_TO_BOSS_DIRECTORY            # pode ser incluido no arquivo ~/.bashrc
export PATH=$BOSSdir/scripts:$BOSSdir/exe:$PATH
```

Para criar o ambiente e instalar:

```bash
conda create --name ligpargen python=3.7
conda activate ligpargen
conda install -c conda-forge rdkit openbabel
```
```bash
cd $HOME
git clone https://github.com/Isra3l/ligpargen.git
pip install -e ligpargen
cd ligpargen
python -m unittest test_ligpargen/test_ligpargen.py
ligpargen -h
```

Para gerar topologia de moléculas, utilize:

```bash
ligpargen -s 'CCO' -n ethanol -p molecule -r ETH -c 0 -o 3 -cgen CM1A-LBCC -verbose -check

ou

ligpargen -s CC(=O)[O-] -n ethanol -p molecule -r CAR -c -1 -o 3 -cgen CM1A -verbose -check
```

[Packmol](https://m3g.github.io/packmol/) é uma biblioteca criada para construir configurações iniciais de sistemas complexos para simulação. Para instalar:
```bash
cd $HOME
python3 -m venv packmol
source $HOME/packmol/bin/activate
pip install packmol
```

---

## :lucide-toolbox: Instalando ferramentas para análises: Alchemlyb/PyMBAR, MDAnalysis, MDTraj, PyEMMA e GMX_MMPBSA.

!!! note

    A adoção de ambientes isolados visa assegurar a manutenção e mitigar incompatibilidades entre bibliotecas.


[Alchemlyb](https://github.com/alchemistry/alchemlyb) é uma biblioteca voltado para análises de energia livres altamente eficiente, utilizando aprendizagem de máquina nas análises. Para instalar:

```bash
conda create -n mbar
conda activate mbar
conda install -c conda-forge alchemlyb pymbar jax jaxlib seaborn "jaxlib=*=*cuda*"
```

[MDAnalysis](https://www.mdanalysis.org/) é "agnóstica" quanto ao formato de arquivo (lê GROMACS, Amber, CHARMM, NAMD, etc. sem precisar converter). É orientada a objetos, permitindo seleções de átomos muito complexas e poderosas. É excelente para escrever ferramentas de análise personalizadas, embora possa ser ligeiramente mais lenta que o MDTraj em cálculos massivos.

```bash
conda create --name mdanalysis
conda activate mdanalysis
conda install -c conda-forge mdanalysis waterdynamics mdaencore
```

[MDTraj](https://www.mdtraj.org/1.9.8.dev0/index.html) projetada para ser extremamente rápida e eficiente em memória, utiliza arrays do NumPy nativamente. É ideal para processar grandes volumes de dados (Big Data) e para converter formatos de trajetória. É frequentemente a escolha preferida para alimentar pipelines de Machine Learning devido à sua integração fácil com o ecossistema Scikit-learn/NumPy.

```bash
conda create --name mdtraj
conda activate mdtraj
conda install -c conda-forge mdtraj
```

[PyEMMA](http://emma-project.org/latest/) usada para analisar a cinética e a termodinâmica de sistemas moleculares. Ela pega dados de simulação (frequentemente processados via MDTraj) e ajuda a identificar estados metaestáveis, barreiras de energia e taxas de transição. É muito usada para entender folding de proteínas ou mudanças conformacionais complexas através de redução de dimensionalidade (TICA).

```bash
conda create --name pyemma
conda activate pyemma
conda install -c conda-forge pyemma
```

[gmx_MMPBSA](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/) utiliza os métodos MM/PBSA (Molecular Mechanics Poisson-Boltzmann Surface Area) e MM/GBSA para calculos de energias livres.

```bash
sudo apt install openmpi-bin libopenmpi-dev openssh-client
conda create -n gmxMMPBSA python=3.11.8
conda activate gmxMMPBSA
conda install -c conda-forge "mpi4py=4.0.1" "ambertools<=23.6"
conda install -c conda-forge numpy matplotlib scipy pandas seaborn
python -m pip install "pyqt6==6.7.1" "parmed"
python -m pip install gmx_MMPBSA

gmx_MMPBSA --version
```
Para configurar o Autocompletion, edite no `.bashrc` e adicione:
```bash
export GMX_COMP_PATH=$HOME/anaconda3/envs/gmxMMPBSA/lib/python3.11/site-packages/GMXMMPBSA/GMXMMPBSA.sh

chmod +x $GMX_COMP_PATH

if [ -f "$GMX_COMP_PATH" ]; then
    source "$GMX_COMP_PATH"
fi
```
Para testar:
```bash
gmx_MMPBSA_test -f $HOME/Documentos -n 16
```

---

### :lucide-flask-conical: *Boas simulações moleculares!*

---
## :lucide-book-open: Leitura complementar

- [How to Install CUDA on Ubuntu](https://linuxcapable.com/how-to-install-cuda-on-ubuntu-linux/)

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
