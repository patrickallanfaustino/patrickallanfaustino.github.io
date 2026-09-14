# Instalação GROMACS 2026.x com ROCm 6.x no Ubuntu 24.04 Noble

!!! info "Testado em"

    - Distro: Ubuntu 24.04.4 (kernel 6.8)
    - GROMACS: 2026.3
    - ROCm: 6.4

!!! warning "Atenção!"

    Este tutorial é baseado em testes realizados em uma máquina com GPU AMD nas condições descritas. Não é garantido que funcione em outras máquinas, distribuições ou versões do Ubuntu. Recomenda-se seguir o tutorial com atenção e realizar backups antes de qualquer alteração no sistema.


## :lucide-laptop: Computador testado e pré-requisitos:
- Verificar minha [Workstation Home](../sobre.md#workstation-home).

Antes de começar, verifique se você atende aos seguintes requisitos:

- Máquina em Linux com distro Ubuntu 24.04 com instalação limpa e atualizado.
- GPU série RDNA2 (testado com arquiteturas RDNA3).
- Documentações [ROCm 6.4](https://rocm.docs.amd.com/projects/install-on-linux/en/docs-6.4.3/index.html), [AdaptiveCpp 25.xx](https://github.com/AdaptiveCpp/AdaptiveCpp) e [GROMACS 2026.x](https://manual.gromacs.org/current/index.html).

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

Verifique a versão do kernel (:lucide-triangle-alert: versão = 6.8) e bibliotecas:
```bash
uname -r
cat /etc/os-release
cmake --version
g++ --version
ldd --version
```

!!! tip "Extra:"

    Para instalar o Kernel GA (General Availability):
    ```bash
    sudo apt install linux-image-generic
    ```

    Para remover kernel antigos incompatíveis:
    ```bash
    dpkg --list | egrep -i --color 'linux-image|linux-headers'
    ```

---
## :lucide-history: Instalando Timeshif
Software para criar snapshots do sistema e restaurar em caso de falhas. Para instalar:
```bash
sudo add-apt-repository ppa:teejee2008/timeshift
sudo apt update
sudo apt install timeshift
```

!!! tip "Extra:"

    Se desejar, instale o GRUB CUSTOMIZER para gerenciar o inicializador e MAINLINE para gerenciar o kernel instalado.

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
## :simple-amd: Instalando ROCm 6.x

Instale o ROCm 6.x seguindo as instruções oficiais da AMD. A instalação ficará em `/opt/rocm`:
```bash
cd ~/Downloads
sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
sudo apt install python3-setuptools python3-wheel
wget https://repo.radeon.com/amdgpu-install/6.4.3/ubuntu/noble/amdgpu-install_6.4.60403-1_all.deb
sudo apt install ./amdgpu-install_6.4.60403-1_all.deb
sudo apt update
sudo amdgpu-install --usecase=rocm,rocmdev,hip,hiplibsdk,openmpsdk,mllib,mlsdk
sudo usermod -a -G render,video $LOGNAME
```
```bash
echo 'ADD_EXTRA_GROUPS=1' | sudo tee -a /etc/adduser.conf
echo 'EXTRA_GROUPS=video' | sudo tee -a /etc/adduser.conf
echo 'EXTRA_GROUPS=render' | sudo tee -a /etc/adduser.conf

reboot
```

Para verificar a instalação, utilize:
```bash
groups
sudo clinfo
sudo rocminfo
sudo rocm-smi
/opt/rocm/bin/hipconfig --full
```

!!! note "Extra:"

    Quando usar `rocminfo`, verificar o nome da placa que será apresentado como `gfx1032` (exemplo RX 6600XT).


Pode ser necessário a instalação da biblioteca rocm-llvm-dev:
```bash
sudo apt install rocm-llvm-dev
```

!!! tip "Dica:"

    Utilize o comando abaixo para listar todos `cases` disponíveis no `amdgpu-install` para instalação:

    ```bash
    sudo amdgpu-install --list-usecase
    ```

    Para remover `amdgpu-install`, utilize:

    ```bash
    sudo amdgpu-install --uninstall --rocmrelease=all
    sudo apt purge amdgpu-install && sudo apt autoremove && sudo apt autoclean

    sudo rm /etc/apt/sources.list.d/amdgpu.list
    sudo rm /etc/apt/sources.list.d/rocm.list
    sudo rm -rf /var/cache/apt/*
    sudo apt clean all
    sudo apt update
    sudo reboot
    ```


---

## :lucide-gauge: Instalando LACT

O aplicativo LACT é utilizado para controlar e realizar overclocking em GPU AMD, Intel e Nvidia em sistemas GNU/Linux.

```bash
cd ~/Downloads
wget https://github.com/ilya-zlobintsev/LACT/releases/download/v0.10.1/lact-0.10.1-0.amd64.ubuntu-2404.deb
sudo dpkg -i lact-0.10.1-0.amd64.ubuntu-2404.deb
sudo systemctl enable --now lactd
```

!!! warning "Atenção!"

    Faça o download do pacote [LACT](https://github.com/ilya-zlobintsev/LACT/releases/) de acordo com a distribuição do Linux.


!!! note "Dica:"

    Para remover versões anteriores, utilize `sudo dpkg -r lact`.

---
## :lucide-thermometer: Instalando Hardware Sensors Indicator

O aplicativo HSI é utilizado para monitorar a temperatura de CPU, GPU, Motherboard, etc. Recomenda-se a instalação pela Central de Aplicativos Snap e configurar para inicialização automatica com monitoramento da CPU (Tctl).
```bash
sudo snap install indicator-sensors
indicator-sensors
```

---

## :lucide-hammer: Instalando AdaptiveCpp 25.x (opcional)

!!! note "Nota:"

    A partir da versão GROMACS 2025.x, há suporte nativo para GPU AMD sem necessidade de instalar o AdaptiveCpp. No entanto, para versões anteriores, é necessário instalar o AdaptiveCpp.

O AdaptiveCpp 25.x trabalha como backend para o GROMACS. Para instalar:

```bash
cd ~/Downloads
git clone https://github.com/AdaptiveCpp/AdaptiveCpp
cd AdaptiveCpp
sudo mkdir build && cd build
```

Para compilar com CMake:
```bash
sudo cmake .. \
-DCMAKE_INSTALL_PREFIX=/usr/local \
-DCMAKE_C_COMPILER=/opt/rocm/llvm/bin/clang \
-DCMAKE_CXX_COMPILER=/opt/rocm/llvm/bin/clang++ \
-DLLVM_DIR=/opt/rocm/llvm/lib/cmake/llvm/ \
-DWITH_ROCM_BACKEND=ON \
-DWITH_SSCP_COMPILER=OFF \
-DWITH_OPENCL_BACKEND=OFF \
-DWITH_LEVEL_ZERO_BACKEND=OFF \
-DWITH_CUDA_BACKEND=OFF \
-DDEFAULT_TARGETS='hip:gfx1032'

sudo make install -j$(nproc)
```

Para verificar a instalação:
```bash
acpp-info
acpp --version
```

---
## :lucide-gem: Instalação do GROMACS 2026.x

Para instalar bibliotecas auxiliares para o GROMACS:
```bash
sudo apt install \
    grace \
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
**LIBTORCH** É possível instalar a biblioteca [libtorch](https://pytorch.org/) para utilizar Redes Neurais.
```bash
mkdir -p ~/software
cd ~/software
wget https://download.pytorch.org/libtorch/cpu/libtorch-shared-with-deps-2.9.0%2Bcpu.zip
unzip libtorch-shared-with-deps-2.9.0+cpu.zip
```

Agora vamos compilar o GROMACS 2026.x com suporte a GPU AMD e Torch (somente CPU):
```bash
cd ~/Downloads
wget ftp://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz
tar -xvf gromacs-2026.3.tar.gz && cd gromacs-2026.3
mkdir -p build && cd build
```

Para compilar:
```bash
sudo cmake .. \
	-DCMAKE_INSTALL_PREFIX=$HOME/software/gromacs-2026.3 \
	-DCMAKE_C_COMPILER=/opt/rocm/bin/amdclang \
	-DCMAKE_CXX_COMPILER=/opt/rocm/bin/amdclang++ \
	-DCMAKE_HIP_COMPILER=/opt/rocm/bin/amdclang++ \
	-DGMX_GPU=HIP \
	-DGMX_HIP_TARGET_ARCH=gfx1032 \
	-DCMAKE_PREFIX_PATH="/opt/rocm;$HOME/software/libtorch" \
    -DGMX_SIMD=AVX2_256 \
	-DGMX_NNPOT=TORCH \
	-DGMX_BUILD_OWN_FFTW=ON \
	-DREGRESSIONTEST_DOWNLOAD=ON \
	-DGMX_HWLOC=ON \
	-DGMX_USE_PLUMED=ON \
	-DGMX_USE_HDF5=ON \
	-DGMX_USE_COLVARS=INTERNAL \
	-DGMX_EXTERNAL_TINYXML2=ON \
	-DGMX_EXTERNAL_ZLIB=ON
```

```bash
make -j$(nproc)
make check -j$(nproc)
make install -j$(nproc)

source $HOME/software/gromacs-2026.3/bin/GMXRC    # configurar no .bashrc
source ~/.bashrc

gmx -version
```

!!! warning "Atenção!"

    Atenção ao `-DHIPSYCL_TARGETS='hip:gfxABC'`, substitua com seus valores para a GPU.


!!! tip "Extra:"

    Para compilar com suporte AdaptiveCpp e Torch (apenas CPU):
    ```bash
    sudo cmake .. \
    -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DCMAKE_C_COMPILER=/opt/rocm/llvm/bin/clang \
    -DCMAKE_CXX_COMPILER=/opt/rocm/llvm/bin/clang++ \
    -DGMX_GPU=SYCL \
    -DGMX_SYCL=ACPP \
    -DCMAKE_INSTALL_PREFIX=$HOME/software/gromacs-2026.3 \
    -DHIPSYCL_TARGETS='hip:gfx1032' \
    -DGMX_SIMD=AVX2_256 \
    -DGMX_HWLOC=ON \
    -DGMX_USE_HDF5=ON \
    -DGMX_USE_PLUMED=ON \
    -DGMX_NNPOT=TORCH \
    -DCMAKE_PREFIX_PATH="$HOME/software/libtorch" \
    -DGMX_USE_COLVARS=INTERNAL \
    -DGMX_EXTERNAL_TINYXML2=ON \
    -DGMX_EXTERNAL_ZLIB=ON
    ```

---

## :lucide-gem: Instalação do OpenMM 8.x

!!! warning "Atenção!"

    Certifique-se de ter o Miniconda instalado.

```bash
conda create --name openmm-conda
conda activate openmm-conda
conda install -c conda-forge openmm-hip openmmforcefields pdbfixer openmm-setup openmmtools pymbar

python -m openmm.testInstallation
```

!!! note "Dica:"

    Para atualizar utilize `conda update --all` e para listar os pacotes instalados `conda list`.
    Para remover o ambiente conda criado `conda env remove --name openmm` e para listar todas os ambientes utilize `conda env list`.

---
## :lucide-eye: Instalando VMD

Instale bibliotecas auxiliares para a representação gráfica molecular:
```bash
sudo apt install \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    ffmpeg \
    vlc
```
```bash
cd ~/software
git clone https://github.com/thesketh/Tachyon.git tachyon
cd tachyon
```

No arquivo Make-config:
```bash
USEJPEG = -DUSEJPEG
JPEGINC = -I/usr/include
JPEGLIB = -ljpeg

USEPNG  = -DUSEPNG
PNGINC  = -I/usr/include
PNGLIB  = -lpng -lz
```

No arquivo Make-arch, localize `linux-64-thr` e acrescentar nas CFLAGS: `-march=znver3 -mtune=znver3`
```bash
cd tachyon/unix
make linux-64-thr
```

!!! note "Dica:"

    O Taychon pode ser obtido [aqui](../assets/instalacao/tachyon.tar.xz).

O VMD permite visualizar moléculas e realizar análises. Para instalação:
```bash
cd ~/software
wget https://www.ks.uiuc.edu/Research/vmd/alpha/vmd-2.0.1a1.bin.LINUXAMD64.tar.gz
tar xvzf vmd-2.0.1a1.bin.LINUXAMD64.tar.gz
cd  vmd-2.0.1a1
```

!!! note "Dica:"

    Verifique o arquivo `configure.options` para configurar o VMD de acordo com sua máquina.
    No arquivo `configure`, altere $install_bin_dir e $install_lib_dir para o diretório de instalação desejado. Por exemplo, para instalar em $HOME/software/vmd

```bash
./configure
cd src
make install -j$(nproc)

vmd
```

## :lucide-eye: Instalando o ChimeraX

O ChimeraX permite visualizar moléculas e realizar análises. Para instalação:
```bash
cd ~/software
wget -O ucsf-chimerax_1.12ubuntu24.04_amd64.deb "https://www.cgl.ucsf.edu/chimerax/cgi-bin/secure/chimerax-get.py?file=1.12/ubuntu-24.04/ucsf-chimerax_1.12ubuntu24.04_amd64.deb"
sudo apt install ~/software/ucsf-chimerax_1.12ubuntu24.04_amd64.deb

chimerax
```

---
## :lucide-calculator: Instalando o Julia

O Julia é uma linguagem de programação voltada para cálculos científicos, similar ao Python. Para instalar:

```bash
mkdir -p ~/software/julia
cd ~/software/julia
curl -fsSL https://install.julialang.org | sh
```

Para atualizar, utilize no terminal `juliaup update`. Para remover utilize `juliaup self uninstall`.

---
## :lucide-book-open: Leitura complementar

- [Install workflow with AMD GPU support (Framework 16, Ubuntu 24.04, GPU: AMD Radeon RX 7700S)](https://gromacs.bioexcel.eu/t/install-workflow-with-amd-gpu-support-framework-16-ubuntu-24-04-gpu-amd-radeon-rx-7700s/10870)

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
