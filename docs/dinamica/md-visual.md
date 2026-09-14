# Renderizar imagens e videos de dinâmicas moleculares

> O objetivo é renderizar imagens e video com qualidade para publicações a partir da dinâmica molecular.
>
> Explore, colabore e estude! :lucide-smile: Dúvidas: [patrick.faustino@unesp.br](mailto:patrick.faustino@unesp.br)


## :lucide-route: Ajuste de trajetória
Para ajustar a trajetória:
```bash
# 1. Periodicidade
gmx trjconv -s md.tpr -f md.xtc -o 1_mol.xtc -pbc mol -center -ur compact
#    grupos: Protein (centro) / System (saída)

# 2. Remover rotação e translação globais
gmx trjconv -s md.tpr -f 1_mol.xtc -o 2_fit.xtc -fit rot+trans
#    grupos: Backbone (ajuste) / System (saída)

# 3. Filtragem passa-baixa com decimação
gmx filter -s md.tpr -f 2_fit.xtc -ol 3_video.xtc -nf 10 -nojump -nofit

```

Para imagens com o ChimeraX, utilize a estrutura mais populosa do cluster:
```bash
gmx cluster -s md.tpr -f 2_fit.xtc -cl clusters.pdb -cutoff 0.15 -method gromos
#   grupos: Protein (ajuste) / Protein (saída)

```

## :lucide-eye: Representação gráfica

=== "Video"

    Para carregar uma trajetória no VMD, utilize o comando:
    ```bash
    vmd md.gro 3_video.xtc
    ```
    O present utilizado abaixo é para melhorar a visualização da molécula e da trajetória:
    ```bash
    Display > Orthographic          # projeção ortográfica, sem distorção de perspectiva
    Display > Rendermode > GLSL
    Display > Axes > Off            # remove os eixos
    Display > Depth Cue > off       # remove a névoa de profundidade
    Display > Display Settings > Shadows > On
    Display > Display Settings > Amb. Occl. > On
    Display > Display Settings > DoF > On
    Graphics > Colors > Display > Background > 8 white
    ```

    Para alterar as representação da molécula, utilize `protein`, `water`, `resname NA` e `resname CL`:
    ```bash
    Selected Atoms: protein; Coloring Method: Secundary Structure; Drawing Method: NewCartoon; Material: AOChalky
    Selected Atoms: water; Coloring Method: ColorId - 22 cyan3; Drawing Method: QuickSurf; Material: Transparent
    Selected Atoms: resname NA; Coloring Method: Name; Drawing Method: Licorice; Material: AOChalky
    Selected Atoms: resname CL; Coloring Method: Name; Drawing Method: Licorice; Material: AOChalky
    ```

    Em Plugins > TkConsole, é possível alterar a resolução da imagem:
    ```bash
    display resize 960 540    # enquadre a molécula na janela.
    ```

    Em File > Save Visualization State, salve o estado da visualização em um arquivo `cena.vmd`.

    Em seguida, no prompt de comando e utilizando [esse arquivo](../assets/dinamica/render_4k_external.tcl), digite:
    ```bash
    vmd -dispdev text -size 3840 2160 -e render_4k_external.tcl
    ```
    
    !!! warning "Atenção!"
        O arquivo `render_4k_external.tcl` deve estar na mesma pasta que o arquivo `cena.vmd`. Caso contrário, o VMD não irá renderizar a imagem.
        Abra e configure corretamente o arquivo `render_4k_external.tcl`.

    Para renderizar o video:
    ```bash
    # em 4K
    ffmpeg -framerate 30 -i frames/f%05d.png -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart video_4k.mp4

    # em 1080p
    ffmpeg -framerate 30 -i frames/f%05d.png -vf "scale=1920:-2:flags=lanczos" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart video_1080p.mp4

    ```

    <div align="center">
        <iframe width="560" height="315" src="https://www.youtube.com/embed/ygxD4YCAXkQ?si=MxXslrvHmzIpHj_U" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
    >O VMD (*Visual Molecular Dynamics*) possui esquema de cores para estruturas de biomoléculas: 🟣 violeta para alfa-hélices; 🟡 amarelo para beta-folhas; 🔵 azul para Hélices 3-10; 🔵 ciano para voltas e ⚪ branco para novelos ou cordas.

=== "Imagem"

    Para a representação gráfica de alta qualidade em artigos, use o ChimeraX. Abra o arquivo `.pdb` e configure no ChimeraX.
    
    !!! note "Dica:"
        Para converter arquivo `.gro` em `.pdb` para uso no ChimeraX, utilize:
        ```bash
        gmx trjconv -s md.tpr -f 2_fit.xtc -o frame_200ns.pdb -dump 200000 -conect
        ```
    
    ```bash
    set bgColor white
    camera ortho
    material dull
    hide solvent; hide H
    view orient

    graphics quality 6
    lighting soft
    lighting depthCue false
    lighting shadows false
    lighting multiShadow 512
    graphics silhouettes true width 3 color gray depthJump 0.02

    cartoon style protein xsection barbell barScale 0.6 modeHelix default arrows false
    cartoon style strand xsection rectangle
    cartoon style sides 24 divisions 20
    ```

    Para ajustar o esquema de cores:
    ```bash
    ==============================
    Nomes de cor (VMD)
    ==============================
    color helix purple
    color strand yellow
    color coil darkgray

    ==============================
    Nomes de cor (Okabe–Ito, recomendado)
    ==============================
    color name okorange #E69F00;
    color name okskyblue #56B4E9;
    color name okgreen #009E73;
    color name okyellow #F0E442;
    color name okblue #0072B2;
    color name okvermillion #D55E00;
    color name okpurple #CC79A7;
    color name neutromid #BBBBBB

    color #1 neutromid
    color helix okorange
    color strand okblue
    color coil neutromid
    color ligand okgreen
    color ligand byhet
    ```

    Para salvar:
    ```bash
    save fig.png width 3200 height 2400 supersample 4 transparentBackground true
    save fig.glb textureColors true     # para blender
    save fig.cxs                        # estado padrão
    ```

    <div align="center">
        <img src="../assets/dinamica/fig.png">
    </div>
    >A paleta Okabe-Ito fornece 8 cores fáceis de distinguir para pessoas com daltonismo (dificuldade para ver certas cores) em gráficos científicos.


---

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
