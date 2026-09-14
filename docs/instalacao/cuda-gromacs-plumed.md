# Instalação do GROMACS 2026.3 com CUDA 13.x e PLUMED 2.x

!!! warning "Atenção!"

    Atualmente, o suporte do PLUMED 2.x para o GROMACS 2026.3 esta **em desenvolvimento**.

## :lucide-gem: Instalação do GROMACS 2026.3

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

**PLUMED 2.x** Para instalar a biblioteca Plumed:
```bash
cd ~/Downloads
wget https://github.com/plumed/plumed2/releases/download/v2.10.1/plumed-src-2.10.1.tgz
tar -xzf plumed-src-2.10.1.tgz
cd plumed-2.10.1
./configure --prefix=$HOME/software/plumed --enable-mpi --enable-modules=all CXX=mpicxx CC=mpicc FC=mpifort
make -j$(nproc)
make install
```
!!! warning "Compatibilidade"

    Na compilação do GROMACS, utilize `-DGMX_THREAD_MPI=OFF`e `-DGMX_MPI=ON`.

Crie um script para carregar o PLUMED quando for necessário:
```bash
cat > ~/software/plumed/env.sh << 'EOF'
export PATH=$HOME/software/plumed/bin:$PATH
export LD_LIBRARY_PATH=$HOME/software/plumed/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$HOME/software/plumed/lib/pkgconfig:$PKG_CONFIG_PATH
export PLUMED_KERNEL=$HOME/software/plumed/lib/libplumedKernel.so
EOF

source ~/software/plumed/env.sh
plumed info --version
which plumed
```

Para compilar o GROMACS 2026.3 com suporte a CUDA 13.x, siga os passos abaixo:
```bash
cd ~/Downloads
wget ftp://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz
tar -xvf gromacs-2026.3.tar.gz && cd gromacs-2026.3
mkdir -p build && cd build
```

Para realizar o patch do GROMACS com o PLUMED:
```bash
cd ..
plumed patch -p --runtime    # use plumed patch -l para ver opções

cd build
```

```bash
cmake .. \
-DCMAKE_INSTALL_PREFIX=$HOME/software/gromacs-2026.3-plumed \
-DCMAKE_PREFIX_PATH="/usr;/usr/local/cuda" \
-DBUILD_SHARED_LIBS=OFF \
-DGMX_MPI=ON \
-DGMX_THREAD_MPI=OFF \
-DGMX_GPU=CUDA \
-DCUDAToolkit_ROOT=/usr/local/cuda \
-DGMX_FFT_LIBRARY=fftw3 \
-DFFTWF_LIBRARY=/usr/lib/x86_64-linux-gnu/libfftw3f.so \
-DFFTWF_INCLUDE_DIR=/usr/include \
-DGMX_BLAS_USER=/usr/lib/x86_64-linux-gnu/openblas-openmp/libopenblas.so \
-DGMX_LAPACK_USER=/usr/lib/x86_64-linux-gnu/openblas-openmp/libopenblas.so \
-DGMX_DEFAULT_SUFFIX=OFF \
-DGMX_SIMD=AVX2_256 \
-DGMX_USE_PLUMED=ON \
-DGMX_HWLOC=ON \
-DGMX_USE_COLVARS=INTERNAL \
-DGMXAPI=OFF \
-DGMX_EXTERNAL_TINYXML2=ON \
-DGMX_EXTERNAL_ZLIB=ON
```

```bash
make -j$(nproc)
make check -j$(nproc)
make install -j$(nproc)

source $HOME/software/gromacs-2026.3-plumed/bin/GMXRC    # configurar no .bashrc
source ~/.bashrc

gmx -version
```

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
