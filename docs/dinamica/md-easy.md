# Dinâmica Molecular Clássica de uma biomolécula em água

!!! warning "Atenção!"
    Página em reformulação.

O objetivo deste tutorial é simular uma biomolécula em caixa periódica com água a 298,15 K e 1 bar, sem potenciais de viés, e obter resultados estatisticamente defensáveis.

Três decisões distinguem uma trajetória que apenas executa de uma trajetória com significado físico:

1. **Como preparar o sistema?** Em dez etapas, e não em três, liberando os graus de liberdade na ordem em que relaxam.
2. **Como determinar o fim da equilibração?** Por um critério numérico, e não pela inspeção visual da curva de densidade.
3. **Quantas simulações realizar?** Uma única trajetória, por mais longa que seja, não permite estimar a própria incerteza.

!!! info "Por que dez etapas?"

    * O solvente se reorganiza em picossegundos; as cadeias laterais, em centenas de picossegundos; a estrutura secundária, em nanossegundos.

    * A remoção simultânea de todas as restrições faz com que a energia liberada no relaxamento de contatos estéricos se dissipe deformando a vizinhança. As restrições escalonadas evitam esse efeito: mantêm fixos os graus de liberdade lentos enquanto os rápidos relaxam, e são reduzidas progressivamente.

    * O custo adicional é da ordem de poucos nanossegundos por réplica, desprezível diante de uma produção de centenas de nanossegundos.


Explore, colabore e estude! :lucide-smile: Dúvidas: [patrick.faustino@unesp.br](mailto:patrick.faustino@unesp.br)

---
## :lucide-download: Arquivos iniciais

Utilize a estrutura da **xilanase** de código [1XNB](https://www.rcsb.org/structure/1XNB) no PDB, resolvida a 1,49 Å. **Dê preferência a estruturas com resolução cristalográfica inferior a 2,5 Å**, que fornecem geometria mais confiável e detalhada, fundamental para a qualidade da simulação. Estruturas preditas também podem ser obtidas no [AlphaFold](https://alphafold.ebi.ac.uk/).

A preparação da estrutura cristalográfica é uma etapa crítica antes de simulações ou de docagem. A reconstrução de resíduos ausentes, com bibliotecas como o [Modeller](https://salilab.org/modeller/) ou servidores como o [SWISS-MODEL](https://swissmodel.expasy.org/), evita lacunas na cadeia polipeptídica e preserva sua integridade física.

Também é necessário atribuir o estado de protonação dos resíduos tituláveis, com o servidor [H++](http://newbiophysics.cs.vt.edu/H++/) ou com ferramentas de linha de comando como o [PROPKA](https://github.com/jensengroup/propka). Estados de protonação incorretos alteram as cargas atribuídas e, consequentemente, as interações eletrostáticas, a rede de ligações de hidrogênio e a estabilidade conformacional do sistema.

!!! note "Dica:"
    Desenvolvi um notebook para realizar esses ajustes na molécula. Faça o download dos arquivos e configure o notebook para o seu sistema.
    [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/patrickallanfaustino/patrickallanfaustino.github.io/blob/main/docs/assets/notebooks/protein_builder.ipynb)

<div align="center">
    <img src="../assets/dinamica/xilanase.png" alt="estrutura cristalográfica da xilanase">
</div>

>Xilanase, 1XNB. O VMD (*Visual Molecular Dynamics*) possui esquema de cores para estruturas de biomoléculas: 🟣 violeta para alfa-hélices; 🟡 amarelo para beta-folhas; 🔵 azul para hélices 3₁₀; 🔵 ciano para voltas e ⚪ branco para novelos ou cordas.


---
## :lucide-atom: Preparo da topologia da molécula: campos de forças

O arquivo **1XNB.pdb** contém, além das coordenadas da biomolécula, moléculas de água (`HOH`) e outros ligantes (`HETATM`). Remova esses componentes para evitar erros nas etapas seguintes, editando o arquivo manualmente ou com os comandos a seguir:

```bash
grep -v HETATM 1XNB.pdb > 1XNB_clean.pdb    # remove ligantes e água

grep -v HOH 1XNB.pdb > 1XNB_clean.pdb       # remove apenas a água
```

Algumas biomoléculas apresentam múltiplas cadeias, identificadas como `chain A`, `chain B` e assim por diante. Defina a(s) cadeia(s) que serão estudadas.

Após a limpeza, ajuste os estados de protonação dos resíduos, de modo que a biomolécula tenha o estado de carga adequado ao pH de interesse.

Em seguida, gere a topologia, escolhendo o campo de força e o modelo de água. Escolha ff19SB + OPC, se possível:

```bash
gmx pdb2gmx -v -f 1XNB_clean.pdb -o xilanase.gro -ignh

# -v = verbose, exibe o andamento do processo.
# -f = arquivo de entrada com as coordenadas.
# -o = arquivo de saída com as coordenadas.
# -ignh = ignora hidrogênios já presentes no arquivo de entrada.
```

!!! note "Dica:"

    Para utilizar um campo de força externo, coloque a pasta correspondente no diretório de trabalho com o nome `<nome>.ff`.


Sem informação adicional, o `pdb2gmx` atribui estados de protonação canônicos a cada aminoácido (pH próximo de 7) e adiciona os hidrogênios correspondentes. Ao final, confira a carga líquida da biomolécula na mensagem `Total charge in system X.000 e`.

Para visualizar no VMD, utilize:

```bash
vmd xilanase.gro
```

!!! note "Nota:"

    Saiba mais sobre [pdb2gmx](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-pdb2gmx.html).

    Serão criados os arquivos:

    - `xilanase.gro`: coordenadas iniciais de cada átomo, com a nomenclatura do campo de força escolhido.

    - `topol.top`: topologia do sistema, com os parâmetros de interação do campo de força.

    - `posre.itp`: topologia auxiliar com as restrições de posição padrão dos átomos pesados.

| Campo de força | Informações | Modelo de água | Interações não ligadas | Referências |
|---|---|---|---|---|
| **OPLS-AA** | Átomo explícito, desenvolvido por Jorgensen para fases condensadas: proteínas, pequenas moléculas e solventes orgânicos (lipídios: variante L-OPLS). A versão mais recente é a OPLS-AA/M, distribuída pelo grupo de Jorgensen também em formato GROMACS; o `oplsaa.ff` do GROMACS é a OPLS-AA/L. | TIP4P (recomendado no `pdb2gmx`); TIP3P também é usado. | `rvdw` 1.0–1.2 nm, PME, `DispCorr = EnerPres` | [Jorgensen et al. 1996](https://doi.org/10.1021/ja9621760)<br>[Robertson et al. 2015](https://doi.org/10.1021/acs.jctc.5b00356) (OPLS-AA/M)<br>[Siu et al. 2012](https://doi.org/10.1021/ct200908r) (L-OPLS) |
| **AMBER** | Proteínas e ácidos nucleicos. O GROMACS traz nativamente amber99sb-ildn, amber14sb e amber19sb, entre outros. Para DNA e RNA, o AMBER recomenda OL15 e OL3. Pequenas moléculas: GAFF/GAFF2 via ACPYPE. | Depende da versão: TIP3P para ff99SB-ILDN e ff14SB; OPC ou OPC3 para ff19SB. | `rvdw` 0.8–1.0 nm (até 1.2 nm), PME, `DispCorr = EnerPres` | [Lindorff-Larsen et al. 2010](https://doi.org/10.1002/prot.22711) (ff99SB-ILDN)<br>[Maier et al. 2015](https://doi.org/10.1021/acs.jctc.5b00255) (ff14SB)<br>[Tian et al. 2020](https://doi.org/10.1021/acs.jctc.9b00591) (ff19SB)<br>[Zgarbová et al. 2015](https://doi.org/10.1021/acs.jctc.5b00716) (OL15)<br>[Zgarbová et al. 2011](https://doi.org/10.1021/ct200162x) (OL3)<br>[Wang et al. 2004](https://doi.org/10.1002/jcc.20035) (GAFF)<br>[Sousa da Silva & Vranken 2012](https://doi.org/10.1186/1756-0500-5-367) (ACPYPE) |
| **CHARMM36/36m** | Átomo explícito; muito detalhado para lipídios, proteínas (C36m) e carboidratos; pequenas moléculas via CGenFF. Port mais recente para GROMACS: fev/2026 (laboratório MacKerell), em versão *force-switch* (`charmm36-feb2026_cgenff-5.0.ff`, padrão) e LJ-PME (`charmm36-feb2026_ljpme_cgenff-5.0.ff`). | TIP3P do CHARMM (com LJ nos H); não substituir pelo TIP3P original. | *Force-switch*: 1.0→1.2 nm, PME com `rcoulomb = 1.2`, `DispCorr = no` em bicamadas. LJ-PME: PME para Coulomb e LJ, corte de 0.9 nm. | [Best et al. 2012](https://doi.org/10.1021/ct300400x) (C36)<br>[Huang et al. 2017](https://doi.org/10.1038/nmeth.4067) (C36m)<br>[Klauda et al. 2010](https://doi.org/10.1021/jp101759q) (lipídios)<br>[Yu et al. 2021](https://doi.org/10.1021/acs.jctc.0c01326) (LJ-PME)<br>[Vanommeslaeghe et al. 2010](https://doi.org/10.1002/jcc.21367) (CGenFF)<br>[MacKerell et al. 1998](https://doi.org/10.1021/jp973084f) (CHARMM22) |
| **GROMOS (54A7)** | Átomo unido: H alifáticos incorporados aos carbonos. Parametrizado contra energias livres de hidratação e solvatação (53A6/54A7). O GROMACS traz 43a1, 43a2, 45a3, 53a5, 53a6 e 54a7. | SPC | Parametrizado com *twin-range* 0.8/1.4 nm e campo de reação (εRF ≈ 62). No GROMACS atual: corte único de 1.4 nm com campo de reação ou PME; o manual alerta que propriedades como a densidade podem diferir. | [Oostenbrink et al. 2004](https://doi.org/10.1002/jcc.20090) (53A5/53A6)<br>[Schmid et al. 2011](https://doi.org/10.1007/s00249-011-0700-9) (54A7)<br>[Tironi et al. 1995](https://doi.org/10.1063/1.469273) (campo de reação) |

| Modelo | Sítios | Descrição | Referências |
|---|---|---|---|
| **SPC** | 3 | Rígido; O–H = 1.0 Å e ângulo tetraédrico de 109.47°. Ajustado à densidade e à energia de vaporização do líquido. Água de referência do GROMOS. | [Berendsen et al. 1981](https://doi.org/10.1007/978-94-015-7658-1_21) |
| **SPC/E** | 3 | SPC reparametrizado com cargas maiores, incluindo na parametrização uma correção pela energia de autopolarização. Melhora densidade e difusão em relação ao SPC. | [Berendsen et al. 1987](https://doi.org/10.1021/j100308a038) |
| **TIP3P** | 3 | Rígido, geometria experimental (0.9572 Å; 104.52°). Padrão do ff14SB; o CHARMM usa versão modificada com LJ nos H. Barato, mas superestima a difusão e subestima a viscosidade. | [Jorgensen et al. 1983](https://doi.org/10.1063/1.445869) |
| **TIP4P** | 4 | Carga negativa num sítio virtual (M) na bissetriz HOH; o oxigênio guarda só o LJ. Variantes: TIP4P-Ew (Ewald), TIP4P/2005 (diagrama de fases), TIP4P/Ice. | [Jorgensen et al. 1983](https://doi.org/10.1063/1.445869)<br>[Horn et al. 2004](https://doi.org/10.1063/1.1683075) (TIP4P-Ew)<br>[Abascal & Vega 2005](https://doi.org/10.1063/1.2121687) (TIP4P/2005)<br>[Abascal et al. 2005](https://doi.org/10.1063/1.1931662) (TIP4P/Ice) |
| **OPC** | 4 | Rígido, 4 pontos e 3 cargas, otimizado para reproduzir um conjunto de propriedades do líquido. Recomendado com ff19SB; custo semelhante ao de outros modelos de 4 pontos. | [Izadi et al. 2014](https://doi.org/10.1021/jz501780a) |
| **OPC3** | 3 | Versão de 3 pontos da mesma abordagem; mais preciso que TIP3P e SPC/E nas propriedades do líquido, com o custo de um modelo de 3 pontos. | [Izadi & Onufriev 2016](https://doi.org/10.1063/1.4960175) |
| **TIP5P** | 5 | Duas cargas negativas em sítios virtuais nos pares isolados do O. Reproduz o máximo de densidade perto de 4 °C; mais caro. Com PME, preferir o TIP5P-E. | [Mahoney & Jorgensen 2000](https://doi.org/10.1063/1.481505)<br>[Rick 2004](https://doi.org/10.1063/1.1652434) (TIP5P-E) |

!!! warning "Atenção!"

    Escolha o campo de força e o modelo de água com base na natureza do sistema e nas propriedades que serão investigadas.

    É fundamental conhecer os formatos de arquivo utilizados pelo GROMACS. Consulte: [File formats topology](https://manual.gromacs.org/current/reference-manual/topologies/topology-file-formats.html) e [File formats](https://manual.gromacs.org/current/reference-manual/file-formats.html).

---
## :lucide-box: Definindo a caixa de simulação: dimensões, solvatação e neutralização

Nesta etapa, definem-se as dimensões da caixa de simulação, adicionam-se as moléculas de água (solvente) e neutraliza-se o sistema.

```bash
gmx editconf -f xilanase.gro -o box.gro -c -d 1.2 -bt dodecahedron

# -c = centraliza a biomolécula na caixa.
# -d = distância mínima, em nm, entre o soluto e as faces da caixa.
# -bt = box type, formato da caixa.
```

Escolha o formato da caixa (`cubic`, `triclinic`, `octahedron` ou `dodecahedron`) de acordo com a geometria da biomolécula. Para solutos aproximadamente globulares, o `dodecahedron` exige cerca de 71 % do volume de uma caixa cúbica com a mesma distância mínima entre imagens periódicas, o que reduz o número de moléculas de água e o custo computacional.

Verifique as dimensões da caixa na saída do programa. A distância mínima entre a biomolécula e as faces da caixa deve estar **entre 1,0 e 2,0 nm**, de modo que o soluto não interaja com as próprias imagens periódicas.

!!! note "Nota:"

    Saiba mais sobre [editconf](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-editconf.html).

    As opções `-d` e `-box` são formas alternativas de dimensionar a caixa. Com `-box`, as arestas são fixadas explicitamente; por exemplo, `-bt cubic -box 10 10 10` gera uma caixa cúbica de 10 nm de aresta, cabendo ao usuário verificar se a margem em torno do soluto é suficiente. Com `-d`, o GROMACS calcula as dimensões a partir da maior extensão do soluto acrescida da distância especificada, o que garante a margem mínima sem volume excedente. Não combine as duas opções.


<div align="center">
    <img src="../assets/dinamica/box.png" alt="caixa de simulação">
</div>

Para visualizar no VMD:

```bash
vmd box.gro

# Extensions > Tk Console > pbc box -color red
```

---
### :lucide-droplets: Solvatação

Em seguida, preencha a caixa com moléculas de água para solvatar a xilanase, de modo que a biomolécula fique imersa em meio aquoso.

```bash
gmx solvate -cp box.gro -cs tip4p.gro -o solvated.gro -p topol.top

# -cp = coordenadas do soluto (geralmente, a proteína).
# -cs = coordenadas do solvente.
# -p = topologia do sistema, atualizada com o número de moléculas de solvente.
```

O GROMACS preenche a caixa com moléculas de água a partir do arquivo `tip4p.gro`, que contém uma caixa pré-equilibrada de água com 4 sítios, e as identifica como o resíduo **SOL**. Confira a quantidade de solvente adicionado na linha `Number of solvent molecules` da saída. Essa informação é atualizada automaticamente na seção `[ molecules ]` do arquivo `topol.top`.

!!! note "Nota:"

    Saiba mais sobre [solvate](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-solvate.html).

    Para modelos de água de 3 sítios, utilize `-cs spc216.gro`.


<div align="center">
    <img src="../assets/dinamica/solvated.png" alt="caixa solvatada">
</div>

### :lucide-scale: Neutralização
A etapa final da preparação da caixa é a adição de íons. Com o somatório de Ewald (PME), um sistema com carga líquida recebe implicitamente um fundo de carga uniforme que o neutraliza, o que pode introduzir artefatos nas energias e na estrutura. Por isso, o sistema é neutralizado com contraíons explícitos.

Antes de executar o `genion`, gere um arquivo binário `.tpr` com as informações do sistema:

```bash
gmx grompp -v -f inputs/ions.mdp -o ions.tpr -c solvated.gro -p topol.top

# -f = arquivo de parâmetros (.mdp).
# -c = coordenadas do sistema.
```

A opção `-f` indica o arquivo [ions.mdp](../assets/dinamica/inputs/ions.mdp), da pasta `inputs/`, que contém os parâmetros desta etapa. Recomenda-se o estudo detalhado das [opções dos arquivos .mdp](https://manual.gromacs.org/current/user-guide/mdp-options.html).

!!! note "Nota:"

    Saiba mais sobre [grompp](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-grompp.html).

    O `grompp` pode emitir avisos (`warnings`), que devem ser analisados um a um. Somente após confirmar que um aviso não compromete a simulação, suprima-o com `-maxwarn x`, em que `x` é o número de avisos a serem ignorados.


O `genion` solicitará o grupo de moléculas que será substituído pelos íons. Selecione o grupo do solvente (**SOL**), digitando o número correspondente.

Adicione os íons para neutralizar o sistema e atingir a concentração salina desejada:

```bash
gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15

# -s = arquivo de entrada da simulação (.tpr) gerado na etapa anterior.
# -pname = nome do cátion, neste caso sódio (NA).
# -nname = nome do ânion, neste caso cloreto (CL).
# -neutral = adiciona contraíons até neutralizar a carga líquida.
# -conc = concentração salina, em mol/L.
```

Sem as opções `-neutral`, `-conc`, `-np` ou `-nn`, o `genion` não adiciona íons. A opção `-neutral` neutraliza a carga líquida, e `-conc 0.15` acrescenta NaCl até 0,15 mol/L, concentração próxima à fisiológica (≈ 0,9 % m/v).

A saída informa `Will try to add XX NA ions and XX CL ions`, com o número de íons adicionados. O arquivo `topol.top` é atualizado com essas quantidades.


!!! note "Nota:"

    Saiba mais sobre [genion](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-genion.html).


---
## :lucide-vibrate: Restrições de posição
As restrições de posição mantêm os átomos da biomolécula próximos de suas posições de referência durante as etapas iniciais. Elas são definidas em arquivos `.itp`, que indicam os átomos restringidos e a constante de força do potencial harmônico aplicado a cada um.

A minimização e as etapas de ajuste de temperatura e pressão são realizadas de forma escalonada. Inicialmente, a biomolécula permanece fortemente restringida, e apenas a água e os íons relaxam. As restrições são então reduzidas progressivamente, permitindo que a biomolécula se acomode ao solvente.

```bash
gmx make_ndx -f neutralized.gro -o index.ndx

gmx genrestr -f neutralized.gro -n index.ndx -o posre_bb.itp -fc 1000 1000 1000    # Escolha 'MainChain'

gmx genrestr -f neutralized.gro -n index.ndx -o posre_sc.itp -fc 1000 1000 1000    # Escolha 'SideChain-H'
```

Esses comandos geram dois arquivos de restrição: `posre_bb.itp`, para os átomos da cadeia principal (*backbone*), e `posre_sc.itp`, para os átomos pesados das cadeias laterais (*side chains*). O valor de 1000 kJ mol⁻¹ nm⁻² é apenas provisório: ele será substituído por variáveis, para que a constante de força possa ser ajustada em cada etapa.

```bash
awk '($1 ~ /^[0-9]+$/ && NF == 5) {printf "%6s %5s %14s %14s %14s\n", $1, $2, "POSRES_FC_BB", "POSRES_FC_BB", "POSRES_FC_BB"; next} {print}' posre_bb.itp > tmp && mv tmp posre_bb.itp

awk '($1 ~ /^[0-9]+$/ && NF == 5) {printf "%6s %5s %14s %14s %14s\n", $1, $2, "POSRES_FC_SC", "POSRES_FC_SC", "POSRES_FC_SC"; next} {print}' posre_sc.itp > tmp && mv tmp posre_sc.itp
```

Verifique se, em `posre_bb.itp` e `posre_sc.itp`, o valor `1000` foi substituído pelas variáveis `POSRES_FC_BB` e `POSRES_FC_SC`, respectivamente. Essas variáveis são definidas na diretiva `define` de cada arquivo `.mdp`, o que permite reduzir as restrições etapa a etapa.

Por fim, inclua `posre_bb.itp` e `posre_sc.itp` no arquivo `topol.top`, para que o GROMACS aplique as restrições durante a simulação.

---
## :lucide-trending-down: Minimização do sistema

A etapa seguinte é a minimização de energia, que remove contatos estéricos desfavoráveis e leva o sistema a um mínimo local de energia potencial antes da dinâmica. Cada etapa consiste em gerar um arquivo `.tpr` com o `grompp` e executá-lo com o `mdrun`.

A minimização é escalonada: as três primeiras etapas restringem a biomolécula com constantes de força decrescentes, de modo que o solvente e os íons relaxem primeiro. A última etapa é realizada sem restrições.

| Etapa | Cadeia principal (kJ mol⁻¹ nm⁻²) | Cadeias laterais (kJ mol⁻¹ nm⁻²) |
|---|---|---|
| em1_rest | 2100 | 2100  |
| em2_rest | 800 | 800  |
| em3_rest | 40 | 40  |
| em4_free | 0 | 0  |

```bash
gmx grompp -v -f inputs/em1_rest.mdp -c neutralized.gro -r neutralized.gro -p topol.top -o em1.tpr
gmx mdrun -v -deffnm em1

gmx grompp -v -f inputs/em2_rest.mdp -c em1.gro -r neutralized.gro -p topol.top -o em2.tpr
gmx mdrun -v -deffnm em2

gmx grompp -v -f inputs/em3_rest.mdp -c em2.gro -r neutralized.gro -p topol.top -o em3.tpr
gmx mdrun -v -deffnm em3

gmx grompp -v -f inputs/em4_free.mdp -c em3.gro -r neutralized.gro -p topol.top -o em4.tpr
gmx mdrun -v -deffnm em4

# -r = coordenadas de referência para as restrições de posição.
# -deffnm = define o nome padrão dos arquivos de entrada e saída.
```

O `mdrun` é o programa que executa a minimização e a dinâmica no GROMACS. A opção `-deffnm` padroniza os nomes dos arquivos de entrada e saída; o nome usado em `grompp -o <nome>.tpr` deve ser o mesmo informado em `-deffnm`.

!!! note "Nota:"

    Saiba mais sobre [mdrun](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-mdrun.html).


Avalie a minimização pela energia potencial da última etapa. Para isso, extraia os dados do arquivo de energia (`.edr`) para um arquivo gráfico (`.xvg`) e verifique se a energia potencial atingiu um patamar. Confira também, na saída do `mdrun`, se a força máxima (`Fmax`) ficou abaixo do critério `emtol` definido no `.mdp`.

```bash
gmx energy -f em4.edr -s em4.tpr -o potential.xvg

xmgrace potential.xvg
```

Quando solicitado, digite o número correspondente a `Potential`, seguido de um espaço e de 0 (zero) para encerrar a seleção. Exemplo: `11 0`.

!!! note "Nota:"

    Saiba mais sobre [energy](https://manual.gromacs.org/documentation/current/onlinehelp/gmx-energy.html).

<div align="center">
    <img src="../assets/dinamica/minim.png" alt="gráfico da energia minimizada">
</div>

---
## :lucide-sliders-horizontal: Equilíbrio NVT e NPT: termostatos e barostatos

As próximas etapas são a equilibração da temperatura e da pressão do sistema. Primeiro, ajuste a temperatura para 298,15 K (25 °C) e, em seguida, a pressão para 1 bar (0,98 atm). Essas condições visam simular um ambiente termodinâmico semelhante ao meio biológico.

### :lucide-thermometer: NVT: ajustando a temperatura da caixa de simulação
Inicie a equilibração de temperatura (ensemble NVT), na qual o número de moléculas (N), o volume (V) e a temperatura (T) são mantidos constantes. Para esta etapa, gere o arquivo binário `.tpr` utilizando o arquivo de parâmetros [nvt.mdp](../assets/dinamica/inputs/nvt.mdp). Este arquivo contém as seguintes definições:

* Define a restrição da biomolécula, com `define = -DPOSRES`.
* Define o tempo para o ajuste da temperatura, em `nsteps = 50000 x 0,002 (dt) = 100 ps`.
* Define o algoritmo para o ajuste da temperatura, em `tcoupl = V-rescale`.
* Define os grupos para o ajuste da temperatura, com `tc-grps = Protein   non-Protein`.
* Define a constante de acoplamento da temperatura, com `tau-t = 1.0`.
* Define a temperatura de referência, em `ref-t = 298.15`.

Algumas considerações específicas:

* **Restrições de Posição**: Utilize restrições de posição para manter os átomos pesados da proteína (não-hidrogênios) "congelados" em suas posições iniciais. Esta técnica é crucial para permitir que as moléculas de água se acomodem e relaxem ao redor da proteína sem desestabilizar a sua estrutura. O arquivo `posre.itp` define a força máxima dessa restrição (padrão de 1000 kJ/mol/nm). Se um átomo sofrer um choque muito forte, a restrição permite que apenas ele se mova ligeiramente para aliviar a tensão, preservando a estabilidade do resto da molécula.

* **Grupos de Temperatura (Termostato)**: Separe o controle de temperatura em dois grupos com o parâmetro `tc-grps = Protein Non-Protein`. Esta abordagem aumenta a precisão e a eficiência do controle de temperatura. Ela permite que o termostato meça e ajuste a temperatura da proteína e do solvente de forma independente, corrigindo as variações térmicas de cada componente com maior acurácia.

* **Constante de Acoplamento da Temperatura (tau-t)**: Ajuste a frequência de atuação do termostato com o parâmetro `tau-t = 1.0`. Este valor, em picossegundos (ps), define a frequência com que o termostato corrige a temperatura do sistema. Mantenha tau-t na faixa de **0,5 a 1,0** ps e certifique-se de que ele seja **sempre menor que a constante de acoplamento da pressão (tau-p)**, que será definida na próxima etapa. Atenção: Evite usar valores muito baixos para tau-t. Isso faria o termostato agir de forma agressiva, o que pode causar instabilidades e levar ao colapso da simulação ("explosão").

```bash
gmx grompp -v -f inputs/nvt.mdp -c em.gro -r em.gro -o nvt.tpr -p topol.top

# -r = restrain file, arquivo de coordenadas com as restrinções iniciais (geralmente mesmo arquivo).
```
```bash
gmx mdrun -v -deffnm nvt
```

Após a equilibração, verifique se a temperatura do sistema se estabilizou corretamente. Para isso, gere e analise o gráfico de temperatura. No gráfico, confirme se a temperatura média corresponde ao valor definido nos parâmetros e observe se as flutuações estão estáveis.

```bash
gmx energy -f nvt.edr -s nvt.tpr -o temperature.xvg
```

Selecione o número correspondente a 'Temperature' seguida por espaço e 0 (zero).

```bash
xmgrace temperature.xvg
```

<div align="center">
<img src="../assets/dinamica/temperature.png" alt="gráfico da temperatura">
</div>

Após 20 ps, observe que a temperatura do sistema estabilizou em 298,15 K. Caso a estabilização não seja alcançada, aumente o valor de `nsteps` e realiza novamente a etapa. Após a temperatura devidamente controlada, procede-se ao ajuste da pressão do sistema.

### :lucide-gauge: NPT: ajustando a pressão da caixa de simulação
Concluída a equilibração da temperatura, inicie a equilibração da pressão (ensemble NPT). Nesta etapa, a densidade do sistema será ajustada para a pressão correta, mantendo-se constantes o número de moléculas (N), a pressão (P) e a temperatura (T). Para isso, gere um novo arquivo binário .tpr utilizando o arquivo de parâmetros [npt.mdp](../assets/dinamica/inputs/npt.mdp). Este arquivo contém as seguintes definições:

* O algoritmo responsável por ajustar a pressão, com `pcoul = C-rescale`.
* A constante de acoplamento da pressão, em `tau-p = 3.0`.
* A pressão de referência, em bar, `ref-p = 1.0`.

Você notará que a maioria dos parâmetros para a etapa NPT é idêntica ou semelhante à da etapa NVT anterior. A principal diferença é que o tempo de simulação para a equilibração de pressão costuma ser maior. É importante destacar que o GROMACS utiliza o estado final da equilibração NVT como o ponto de partida para esta nova etapa. Esse encadeamento garante a continuidade do processo, aplicando agora as novas condições de pressão constante.

```bash
gmx grompp -v -f inputs/npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -o npt.tpr -p topol.top

# -t = time file, arquivo com checkpoint anterior (geralmente utilizado para indicar o ponto de partida com relação a dinâmica anterior)
```
```bash
gmx mdrun -v -deffnm npt
```
```bash
gmx energy -f npt.edr -s npt.tpr -o pressure.xvg
gmx energy -f npt.edr -s npt.tpr -o density.xvg
```

<div align="center">
<img src="../assets/dinamica/pressure.png" alt="gráfico da pressão">
</div>
<div align="center">
<img src="../assets/dinamica/density.png" alt="gráfico da densidade">
</div>

Para avaliar a equilibração da pressão, evite focar no gráfico de pressão, pois suas flutuações são geralmente muito altas e pouco informativas. Em vez disso, analise o gráfico de densidade, que é o indicador correto para esta etapa. No gráfico, verifique se a curva se estabiliza em um valor médio, apresentando apenas pequenas variações. Essa estabilização confirma que o sistema atingiu a densidade correta e está em equilíbrio.

A seguir, apresentamos um breve resumo dos principais termostatos e barostatos disponíveis para controlar a temperatura e a pressão em suas simulações.

| Termostato | Características | Vantagens | Limitações
|--------|---------|-------------|---------------|
| **Berendsen** | Rápido para equilibrar temperatura | Simples e eficiente para equilíbrios | Não reproduz corretamente as flutuações canônicas |
| **V-rescale*** | Mantém temperatura média correta e flutuações realistas | Estável e mais preciso que Berendsen | Ligeiramente mais complexo |
| **Nose-Hoover** | Mantém distribuição canônica (NVT) | Correto estatisticamente | Pode ter acoplamento mais lento |

| Barostato | Características | Vantagens | Limitações
|--------|---------|-------------|---------------|
| **Berendsen** | Ajusta pressão rapidamente durante o equilíbrio | Simples, ideal para pré-produção | Não reproduz corretamente as flutuações canônicas |
| **Parrinello-Rahman** | Permite flutuações de volume e forma da caixa (NPT) | Correto para simulações de produção | Pode ser instável sem bom equilíbrio inicial |
| **C-rescale*** | Versão estocástica rigorosa de controle de pressão. Mantém flutuações canônicas corretas no ensemble NPT | Produz NPT canônico exato, mais robusto e estável que Parrinello-Rahman em algumas situações | Disponível a partir do GROMACS 2023, pouco testado em comparação com Parrinello-Rahman |

!!! warning

    A escolha do termostato e barostato deve considerar a natureza do sistema e as propriedades que se deseja investigar.

    O GROMACS recomenda: **V-rescale** e **C-rescale**.


!!! tip

    Verifique a performance na mensagem de saída, pode ser útil para planejar o tempo da simulação baseado no seu computador. Exemplo: 995.45 ns/day ou 0.024 hour/ns.


## :lucide-play: Produção: integradores
A etapa final é a simulação de produção. Se todos os passos anteriores foram concluídos sem erros, seu sistema foi preparado corretamente e a simulação de produção tem grandes chances de ser bem-sucedida. Durante a execução, que pode ser longa, monitore a carga de trabalho (CPU/GPU) e a temperatura do seu computador, pois problemas externos de hardware ou software ainda podem interromper o processo.

Inicie a simulação de produção. Primeiro, gere o arquivo de entrada binário (.tpr) com base no arquivo de parâmetros [md.mdp](../assets/dinamica/inputs/md.mdp). Logo depois, inicie a simulação final de dinâmica molecular executando o comando a partir desse arquivo `.tpr`.

```bash
gmx grompp -v -f inputs/md.mdp -c npt.gro -t npt.cpt -o md_5ns.tpr -p topol.top

gmx mdrun -v -deffnm md_5ns
```
Pontos importantes sobre os parâmetros da simulação de produção:

- **Remoção das Restrições de Posição**: Diferentemente das etapas de equilibração, remova todas as restrições de posição da biomolécula. Agora que o sistema está equilibrado, o objetivo é permitir que a molécula se mova e se comporte livremente, sob a influência apenas das forças físicas do sistema. É nesta fase que observamos a dinâmica "natural" da biomolécula, o que caracteriza a simulação de produção.

- **Seleção do Integrador (`integrator = md`)**: A escolha do algoritmo (integrador) que calcula o movimento dos átomos é crucial. Para simulações de produção padrão, utilize o integrador `md`. Este integrador, que implementa o algoritmo Leap-Frog, é altamente eficiente e otimizado no GROMACS para performance e precisão. Embora existam outros integradores, como o `sd` (Dinâmica Estocástica), eles são geralmente aplicados em contextos específicos, como cálculos de energia livre.

| Integrador     | Características                          | Vantagens                          | Limitações / Quando evitar                   | Uso típico                                    |
|----------------|------------------------------------------|------------------------------------|----------------------------------------------|-----------------------------------------------|
| **md***         | Leap-frog Verlet. Passo de tempo curto (1–2 fs). Conserva bem energia e momento.         | Robusto, padrão, eficiente.        | Velocidades não coincidem com posições.      | Produção em proteínas, membranas, solventes.  |
| **md-vv**      | Velocity-Verlet. Calcula velocidades no mesmo ponto que posições.                         | Melhora cálculo de velocidades.    | Pouco ganho em muitos casos.                 | Transporte, difusão, análise energética.      |
| **md-vv-avek** | Velocity-Verlet com controle de energia cinética média (AVEK). | Temperatura estável sem termostato.| Mais pesado; pouco usado.                    | Equilíbrios longos sensíveis a flutuações.    |
| **sd**         | Dinâmica de Langevin (stochastic). Força de fricção + ruído gaussiano..            | Excelente controle térmico.        | Distorce dinâmica real em excesso.           | Sistemas viscosos, líquidos iônicos, membranas.|
| **bd**         | Dinâmica Browniana (Langevin overdamped). Ignora momento, apenas difusão.        | Simples e estável.                 | Perde informação de movimento rápido.        | Difusão lenta, modelos grosseiros (CG).       |
| **steep**      | Minimização por gradiente descendente. Desce na direção de maior inclinação.   | Rápido para remover contatos ruins.| Convergência lenta perto do mínimo.          | Pré-MD, relaxamento inicial.                  |
| **cg**         | Minimização gradiente conjugado.         | Mais eficiente que *steep*.        | Menos robusto no início.                     | Refinar após steep.                           |
| **l-bfgs**     | Minimização quasi-Newton.                | Muito rápido em sistemas pequenos. | Ineficiente em sistemas grandes.             | Clusters ou moléculas pequenas.               |

!!! note

    O GROMACS salva checkpoint da dinâmica molecular a cada 15 minutos em um arquivo `.cpt`. Esse tempo pode ser alterado com a tag `-cpt [x]`.


Caso sua simulação seja interrompida por algum problema, retome-a a partir do último ponto salvo (checkpoint). Para fazer isso, adicione a flag `-cpi` ao seu comando `mdrun`, especificando o nome do arquivo de checkpoint:
```bash
gmx mdrun -v -deffnm md_5ns -cpi md_5ns.cpt

# -cpi = checkpoint, arquivo com o ultimo estado salvo (backup).
```

Para estender o tempo de uma simulação que já foi concluída, acrescentando mais tempo:
```bash
gmx convert-tpr -s md_5ns.tpr -extend 5000 -o md_10ns.tpr

# -extend = indica o tempo, em ps, a ser acrescentado.
```
```bash
gmx mdrun -v -deffnm md_10ns -cpi md_5ns.cpt -noappend
```
```bash
gmx trjcat -f md_5ns.xtc md_10ns.part0002.xtc -o final.xtc
```

!!! note

    Saiba mais sobre [convert-tpr](https://manual.gromacs.org/current/onlinehelp/gmx-convert-tpr.html).


Link para visualizar o video demonstrativo da dinâmica: [https://youtu.be/IQGiznRc0Xo](https://youtu.be/IQGiznRc0Xo).

- [Imagens e video](md-visual.md)
- [Análises de resultados](md-analysis.md)

---

## :lucide-clipboard-list: Resumo

```
grep -v HETATM 1S0Q.pdb > 1S0Q_clean.pdb
gmx pdb2gmx -v -f 1S0Q_clean.pdb -o tripsina.gro
```
```bash
gmx editconf -f tripsina.gro -o box.gro -c -d 1.0 -bt cubic
gmx solvate -cp box.gro -cs spc216.gro -o solvated.gro -p topol.top
gmx grompp -v -f inputs/ions.mdp -o ions.tpr -c solvated.gro -p topol.top
gmx genion -s ions.tpr -o solvated_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15
```
```bash
gmx grompp -v -f inputs/minim.mdp -c solvated_ions.gro -o em.tpr -p topol.top
gmx mdrun -v -deffnm em
gmx energy -f em.edr -s em.tpr -o potential.xvg
xmgrace potential.xvg
```
```bash
gmx grompp -v -f inputs/nvt.mdp -c em.gro -r em.gro -o nvt.tpr -p topol.top
gmx mdrun -v -deffnm nvt
gmx energy -f nvt.edr -s nvt.tpr -o temperature.xvg
xmgrace temperature.xvg
```
```bash
gmx grompp -v -f inputs/npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -o npt.tpr -p topol.top
gmx mdrun -v -deffnm npt
gmx energy -f npt.edr -s npt.tpr -o pressure.xvg
xmgrace pressure.xvg
gmx energy -f npt.edr -s npt.tpr -o density.xvg
xmgrace density.xvg
```
```bash
gmx grompp -v -f inputs/md.mdp -c npt.gro -t npt.cpt -o md_5ns.tpr -p topol.top
gmx mdrun -v -deffnm md_5ns
```

---

## :lucide-file-text: Preprint e publicação relacionada

Este tutorial também serve como material suplementar do artigo
relacionado a esta dinâmica molecular.

!!! warning "Em construção"

    Preprint e publicação serão adicionados aqui assim que disponíveis.

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
