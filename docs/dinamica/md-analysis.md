# Análises de Resultados de Dinâmica Molecular

!!! abstract "O que esperar?"
 
    A xilanase GH11 de *Bacillus circulans* (BcX, PDB 1XNB) é uma proteína pequena e rígida, enovelada em folha-β. Por isso, o esperado é uma estrutura global estável e próxima do cristal, com flexibilidade concentrada em poucas alças (sobretudo o *thumb*), e um solvente que reproduz as propriedades do modelo de água OPC. As cinco réplicas devem concordar nas médias e divergir nos eventos raros.

> Explore, colabore e estude! :lucide-smile: Dúvidas: [patrick.faustino@unesp.br](mailto:patrick.faustino@unesp.br)

Esta página analisa as cinco réplicas de 300 ns da [DM não enviesada da xilanase](md-easy.md). Os resultados estão agrupados em seis conjuntos:
 
1. [Preparação e equilibração](#preparacao-e-equilibracao).
2. Estacionariedade e réplicas.
3. Estrutura global comparada ao cristal.
4. Flexibilidade.
5. Sítio ativo.
6. Solvente.

---
## :lucide-flask-conical: Preparação e equilibração

A Figura 1 resume a escada de preparação em três painéis:
 
- **A**, a energia potencial ao longo das quatro minimizações;
- **B**, a temperatura nas etapas de dinâmica, com a rampa nominal de 50 → 298,15 K;
- **C**, a constante de força das restrições em cada etapa, no esqueleto e nas cadeias laterais.

<div align="center">
    <iframe src="../assets/plots/etapas_equilibracao.html" width="100%" height="1000px" style="border:none;" loading="lazy"></iframe>
</div>

**Figura 1.** Escada de preparação da réplica 1: minimização (A), temperatura (B) e restrições posicionais (C). No painel C, em escala logarítmica, as etapas sem restrição (k = 0) são representadas em k = 1.
 
O que a figura mostra:
 
- **Minimização:** dentro de cada etapa, a energia cai de forma monotônica, até cerca de −4,5 × 10⁵ kJ mol⁻¹, em aproximadamente 3400 passos somados. A EM4, sem restrições, converge rapidamente, sinal de que as etapas restritas já haviam removido os contatos ruins.
- **Saltos entre etapas:** o salto entre EM1 e EM2, de cerca de 2 × 10⁴ kJ mol⁻¹, coincide com a troca do modelo de água, flexível na EM1 (`-DFLEXIBLE`) e rígida a partir da EM2. Os saltos seguintes, sem essa troca, são de apenas cerca de 150 kJ mol⁻¹, ordem de grandeza compatível com o arredondamento das coordenadas no `.gro` (0,001 nm).
- **Temperatura:** acompanha a rampa sem atraso apreciável, como esperado com `gen-temp` igual ao primeiro ponto da rampa e `tau-t` de 0,5 ps, e flutua em torno de 298 K da NVT2 em diante.

O comportamento é coerente com o protocolo do tutorial, adaptado de [Roe e Brooks (2020)](https://doi.org/10.1063/5.0013849). A rampa de aquecimento é uma dessas adaptações, pois o protocolo original gera as velocidades já na temperatura-alvo. O aquecimento sem degrau inicial é o sinal, descrito na [etapa NVT1](md-easy.md#nvt1-aquecimento), de uma escolha correta de `gen-temp`.

---

## :lucide-quote: Como citar

FAUSTINO, P. A. S. *Documentação sobre Química Biofísica Computacional*. [S. l.]: Zenodo, 2026. DOI 10.5281/zenodo.22729510. Disponível em: <https://doi.org/10.5281/zenodo.22729510>.
