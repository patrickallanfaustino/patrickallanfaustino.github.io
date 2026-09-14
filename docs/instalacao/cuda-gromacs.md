# Instalação do GROMACS 2026.x e CUDA 13.x

!!! info "Testado em"

    **Ubuntu 24.04.4** (kernel 6.17)

    - GROMACS: 2026.3
    - CUDA: 13.3

    **Ubuntu 26.04.1** (kernel 7.0)

    - GROMACS: 2026.3
    - CUDA: 13.4

## :lucide-laptop: Computador testado e pré-requisitos:
- Verificar minha [Workstation Home](../sobre#workstation-home).

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

!!! tip "Extra:"

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
## :lucide-history: Instalando Timeshif
Software para criar snapshots do sistema e restaurar em caso de falhas. Para instalar:

=== "Ubuntu 26.04"

    ```bash
    sudo apt update
    sudo apt install timeshift
    ```

=== "Ubuntu 24.04"

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
## :simple-nvidia: Instalando CUDA 13.x

=== "Ubuntu 26.04"

    Verifique a compatibilidade da GPU antes. Para CUDA 12 ou superior, requer arquitetura Maxwell ou superior.
    ```bash
    lspci | grep -i nvidia
    ```

    Remova todos os driver relacionados que tiver instalado:
    ```bash
    sudo apt remove --purge "*cuda*" "*cublas*" "*cufft*" "*cufile*" "*curand*" "*cusolver*" "*cusparse*" "*gds-tools*" "*npp*" "*nvjpeg*" "nsight*" "*nvvm*" "*nvidia*"
    sudo apt autoremove --purge
    ```

    Instale os pre-requisitos para CUDA:
    ```bash
    sudo apt update
    sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
    sudo apt install \
        gcc \
        build-essential \
        ca-certificates \
        dkms \
        wget 
    ```

    Adicionar o repositório oficial NVIDIA CUDA:
    ```bash
    cd ~/Downloads
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2604/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    
    sudo apt update
    sudo apt install cuda-toolkit nvidia-open    # nvidia-drivers
    ```

    Para configurar o compilador NVCC, edite o `~/.bashrc` e adicione as linhas abaixo:
    ```bash
    export CUDA_HOME=/usr/local/cuda
    export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
    export PATH=$CUDA_HOME/bin:$PATH
    
    source ~/.bashrc
    reboot
    ```

    Para verificar a instalação, utilize:
    ```bash
    nvidia-smi
    nvcc --version
    ```

    !!! note "Dica:"

        Para remover, utilize:

        ```bash
        sudo apt remove --purge "*cuda*" "*nvidia*" cuda-keyring
        sudo apt purge && sudo apt autoremove && sudo apt autoclean
        sudo rm -f /etc/apt/preferences.d/cuda-repository-pin-600
        sudo rm -f /etc/apt/sources.list.d/cuda*.list
        sudo rm -rf /var/cache/apt/*
        sudo apt clean all
        sudo apt update
        sudo reboot
        ```


=== "Ubuntu 24.04"
    
    Para compilar o CUDA 13.x no Ubuntu 24.04, siga os mesmos passos do Ubuntu 26.04, mas utilize o repositório oficial NVIDIA CUDA para Ubuntu 24.04:
    ```bash
    cd ~/Downloads
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    
    sudo apt update
    sudo apt install cuda-toolkit nvidia-open    # nvidia-drivers
    ```

---
## :lucide-gauge: Instalando LACT

O aplicativo LACT é utilizado para controlar e realizar overclocking em GPU AMD, Intel e Nvidia em sistemas GNU/Linux.

=== "Ubuntu 26.04"

    ```bash
    cd ~/Downloads
    wget https://github.com/ilya-zlobintsev/LACT/releases/download/v0.10.1/lact-0.10.1-0.amd64.ubuntu-2604.deb
    sudo dpkg -i lact-0.10.1-0.amd64.ubuntu-2604.deb
    sudo systemctl enable --now lactd
    ```

=== "Ubuntu 24.04"

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

=== "Ubuntu 26.04"

    **CP2K 2026.x** Para instalar a biblioteca CP2K (QM/MM):

    !!! note "Dica:"

        Se necessário, para corrigir problemas com OpenGL utilize `export HWLOC_COMPONENTS=-gl`.

    !!! warning "Compatibilidade"

        Para usar GROMACS + CP2K para QM/MM, é necessário o uso em comum das bibliotecas fftw3 e openblas.
    
    ```bash
    sudo apt install libopenblas0-openmp libopenblas-openmp-dev

    sudo update-alternatives --config libopenblas.so.0-x86_64-linux-gnu
    sudo update-alternatives --config libblas.so.3-x86_64-linux-gnu
    sudo update-alternatives --config liblapack.so.3-x86_64-linux-gnu

    # e os grupos de desenvolvimento, se existirem:
    sudo update-alternatives --config libopenblas.so-x86_64-linux-gnu
    sudo update-alternatives --config libblas.so-x86_64-linux-gnu
    sudo update-alternatives --config liblapack.so-x86_64-linux-gnu

    sudo ldconfig
    ```

    ```bash
    cd ~/Downloads
    wget https://github.com/cp2k/cp2k/releases/download/v2026.2/cp2k-2026.2.tar.bz2
    tar -xjf cp2k-2026.2.tar.bz2
    cd ~/Downloads/cp2k-2026.2/tools/toolchain

    ./install_cp2k_toolchain.sh \
    -j$(nproc) \
    --with-openblas=system \
    --with-fftw=system \
    --with-openmpi=system \
    --with-scalapack=install \
    --with-elpa=install \
    --with-cosma=install \
    --with-libxsmm=install \
    --with-libxc=install \
    --with-libint=install \
    --with-plumed=install \
    --with-gsl=install \
    --with-libvdwxc=no \
    --with-spglib=no \
    --with-hdf5=no \
    --with-spfft=no \
    --with-libvori=no \
    --with-sirius=no \
    --enable-cuda=no

    ./build_cp2k.sh -j$(nproc) --prefix ~/software/cp2k-2026.2/install

    source $HOME/software/cp2k-2026.2/install/cp2k_env    # configurar no .bashrc
    source ~/.bashrc

    which cp2k.psmp
    cp2k.psmp --version
    ```

    !!! note "Dica:"

        Para instalar o Openblas com o CP2K, utilize `--with-openblas=install` e descubra o diretório de instalação do Openblas com `find ~/software/cp2k-2026.2/install -name "libopenblas.so"`. Utilize o diretório para configurar o GROMACS com `-DGMX_BLAS_USER=/path/to/openblas/lib/libopenblas.so` e `-DGMX_LAPACK_USER=/path/to/openblas/lib/libopenblas.so`.

    Agora, instale o GROMACS 2026.x com suporte a CUDA e CP2K:

    ```bash
    cd ~/Downloads
    wget ftp://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz
    tar -xvf gromacs-2026.3.tar.gz && cd gromacs-2026.3
    mkdir -p build && cd build
    ```

    ```bash
    cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/software/gromacs-2026.3-qmmm \
    -DCMAKE_PREFIX_PATH="/usr;/usr/local/cuda" \
    -DBUILD_SHARED_LIBS=OFF \
    -DGMX_MPI=ON \
    -DGMX_GPU=CUDA \
    -DCUDAToolkit_ROOT=/usr/local/cuda \
    -DGMX_FFT_LIBRARY=fftw3 \
    -DFFTWF_LIBRARY=/usr/lib/x86_64-linux-gnu/libfftw3f.so \
    -DFFTWF_INCLUDE_DIR=/usr/include \
    -DGMX_BLAS_USER=/usr/lib/x86_64-linux-gnu/openblas-openmp/libopenblas.so \
    -DGMX_LAPACK_USER=/usr/lib/x86_64-linux-gnu/openblas-openmp/libopenblas.so \
    -DGMX_CP2K=ON \
    -DCP2K_DIR=$HOME/software/cp2k-2026.2/install/lib \
    -DGMX_DEFAULT_SUFFIX=OFF \
    -DGMX_SIMD=AVX2_256 \
    -DGMX_HWLOC=ON \
    -DGMX_USE_COLVARS=INTERNAL \
    -DGMX_USE_PLUMED=ON \
    -DGMXAPI=OFF \
    -DGMX_INSTALL_NBLIB_API=OFF \
    -DMPI_C_COMPILER=$(which mpicc) \
    -DMPI_CXX_COMPILER=$(which mpicxx) \
    -DMPI_Fortran_COMPILER=$(which mpif90) \
    -DGMX_USE_HDF5=ON \
    -DGMX_EXTERNAL_TINYXML2=ON \
    -DGMX_EXTERNAL_ZLIB=ON
    ```
    
    ```bash
    make -j$(nproc)
    make check -j$(nproc)
    make install -j$(nproc)

    source $HOME/software/gromacs-2026.3-qmmm/bin/GMXRC    # configurar no .bashrc
    source ~/.bashrc

    gmx -version
    ```

=== "Ubuntu 24.04"

    **LIBTORCH** É possível instalar a biblioteca [libtorch](https://pytorch.org/) para utilizar Redes Neurais.
    ```bash
    mkdir -p ~/software
    cd ~/software
    wget https://download.pytorch.org/libtorch/cu130/libtorch-shared-with-deps-2.10.0%2Bcu130.zip
    unzip libtorch-shared-with-deps-2.10.0+cu130.zip
    ```

    ```bash
    cd ~/Downloads
    wget ftp://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz
    tar -xvf gromacs-2026.3.tar.gz && cd gromacs-2026.3
    mkdir -p build && cd build
    ```

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
    -DCMAKE_INSTALL_PREFIX=$HOME/software/gromacs-2026.3 \
    -DGMX_HWLOC=ON \
    -DGMX_USE_HDF5=ON \
    -DGMX_USE_PLUMED=ON \
    -DGMX_USE_COLVARS=INTERNAL \
    -DGMX_NNPOT=TORCH \
    -DGMX_EXTERNAL_TINYXML2=ON \
    -DGMX_EXTERNAL_ZLIB=ON \
    -DCMAKE_PREFIX_PATH="$HOME/software/libtorch;/usr/local/cuda"
    ```

    ```bash
    make -j$(nproc)
    make check -j$(nproc)
    make install -j$(nproc)

    source $HOME/software/gromacs-2026.3/bin/GMXRC    # configurar no .bashrc
    source ~/.bashrc

    gmx -version
    ```

---

## :lucide-gem: Instalação do OpenMM 8.x

!!! warning "Atenção!"

    Certifique-se de ter o Miniconda instalado.

```bash
conda create --name openmm
conda activate openmm
conda install -c conda-forge openmm openmmforcefields pdbfixer openmm-setup flask openmmtools pymbar

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

- [How to Install CUDA on Ubuntu](https://linuxcapable.com/how-to-install-cuda-on-ubuntu-linux/)
- [Compiling Gromacs with CP2K for QMMM simulation](https://freezing.cool/notes/compile-gmx-with-cp2k/)

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
