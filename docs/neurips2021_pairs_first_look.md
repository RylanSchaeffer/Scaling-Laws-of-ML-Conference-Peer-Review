# NeurIPS 2021 consistency experiment: first look at the public pairs

Source: OpenReview's own record, pulled 2026-10-14 (`scripts/fetch_openreview_neurips2021.py`), paired by the `consistency_experiment` field of each decision note (`scripts/build_neurips2021_pairs.py`). The title match gives the same 301 pairs. Reconciliation with the report's Table 1: `data/paired_reviews/neurips2021_reconciliation.md` (exact, up to the 4 fatal-flaw rejections the report describes, which are private).

## What is public

- 309 pairs with at least one public copy; 301 with both copies public; 2340 reviews in those 301 pairs.
- Per copy: every review (rating 1 to 10, confidence 1 to 5, summary, main review, limitations, ethics flags, time spent), the meta-review, the author responses and the reviewer–author discussion, that committee's own decision and the other committee's recommendation.
- Ratings are the final values after the rebuttal. The initial values exist as note revisions on OpenReview and can be pulled.
- Not public: the 451 pairs rejected by both committees whose authors did not opt in, the 4 fatal-flaw rejections, reviewer identities and the reviewer–area chair discussion.

## Decisions of the two committees (both copies public)

Rows: the copy with the lower paper number; columns: the other copy. The public record does not say which copy was the original.

| | oral | spotlight | poster | reject |
|---|---|---|---|---|
| oral | 0 | 0 | 1 | 0 |
| spotlight | 0 | 3 | 8 | 10 |
| poster | 5 | 8 | 74 | 92 |
| reject | 0 | 15 | 82 | 3 |

Accepted by both: 99. Accepted by one: 199. Rejected by both (opted in): 3.

## Mean final rating, side against side

- Absolute gap between the two committees' mean ratings: mean 0.97, median 0.75; at least 1 point in 46% of pairs, at least 2 in 13%.
- Correlation of the two mean ratings: r = -0.13. This set is selected on acceptance by at least one committee, which depresses the correlation; the report's Figure 1, on all 764 decided papers, is the unbiased version.
- Among the 199 split pairs, the accepting committee's mean rating exceeds the rejecting committee's in 94% of pairs.

## The oral and spotlight pairs

Every pair in which at least one committee recommended an oral or a spotlight. All are public. Links open the two forums.

| Pair | Lower-number copy | Other copy | Mean ratings | Reviews | Title |
|---|---|---|---|---|---|
| n21-048 | [poster](https://openreview.net/forum?id=kt_s_ZbYvtP) | [oral](https://openreview.net/forum?id=wfJCeMS-jH) | 6.00 vs 7.00 | 4 + 3 | Causal Identification with Matrix Equations |
| n21-090 | [poster](https://openreview.net/forum?id=GvU4RvMwlGo) | [oral](https://openreview.net/forum?id=4JHdr4lgpVT) | 6.67 vs 6.50 | 3 + 4 | Coresets for Decision Trees of Signals |
| n21-083 | [spotlight](https://openreview.net/forum?id=AAWuCvzaVt) | [spotlight](https://openreview.net/forum?id=OU98jZWS3x_) | 7.50 vs 7.50 | 4 + 4 | Diffusion Models Beat GANs on Image Synthesis |
| n21-133 | [spotlight](https://openreview.net/forum?id=rMKTq-ca0qu) | [spotlight](https://openreview.net/forum?id=vPVTsuJtGky) | 6.25 vs 7.00 | 4 + 5 | Early-stopped neural networks are consistent |
| n21-301 | [oral](https://openreview.net/forum?id=an8FSGbuCw) | [poster](https://openreview.net/forum?id=IVV1putQ90) | 8.00 vs 6.67 | 4 + 3 | Latent Equilibrium: A unified learning theory for arbitrarily fast computation with arbitrarily slow neurons |
| n21-002 | [poster](https://openreview.net/forum?id=kwN2xvZ2XZ9) | [oral](https://openreview.net/forum?id=5JvnsAdf6Vz) | 7.00 vs 7.75 | 3 + 4 | Learning Frequency Domain Approximation for Binary Neural Networks |
| n21-168 | [poster](https://openreview.net/forum?id=VXeoK3fJZhW) | [oral](https://openreview.net/forum?id=UVQNdLIELSU) | 7.33 vs 8.00 | 3 + 4 | Replacing Rewards with Examples: Example-Based Policy Search via Recursive Classification |
| n21-186 | [poster](https://openreview.net/forum?id=Kvb0482Ysaf) | [oral](https://openreview.net/forum?id=o6-k168bBD8) | 7.00 vs 7.40 | 4 + 5 | Sequential Causal Imitation Learning with Unobserved Confounders |
| n21-294 | [spotlight](https://openreview.net/forum?id=7pU_P1IbePx) | [spotlight](https://openreview.net/forum?id=neRSyESg1GU) | 7.75 vs 7.50 | 4 + 4 | Statistical Query Lower Bounds for List-Decodable Linear Regression |
| n21-028 | [spotlight](https://openreview.net/forum?id=ehzq1YQrucI) | [poster](https://openreview.net/forum?id=J-pFhOiGVn7) | 7.00 vs 6.75 | 4 + 4 | An Infinite-Feature Extension for Bayesian ReLU Nets That Fixes Their Asymptotic Overconfidence |
| n21-127 | [poster](https://openreview.net/forum?id=PYJnWEn-uMn) | [spotlight](https://openreview.net/forum?id=6tGP5Z-QbMb) | 5.75 vs 6.75 | 4 + 4 | An Uncertainty Principle is a Price of Privacy-Preserving Microdata |
| n21-057 | [poster](https://openreview.net/forum?id=4QrgRSAAroI) | [spotlight](https://openreview.net/forum?id=i2bTx7ZWFfI) | 6.50 vs 6.80 | 4 + 5 | Bandit Learning with Delayed Impact of Actions |
| n21-023 | [poster](https://openreview.net/forum?id=7_M2f2DEIEK) | [spotlight](https://openreview.net/forum?id=eIdzV1-Jdwv) | 7.25 vs 7.75 | 4 + 4 | Beyond Tikhonov: faster learning with self-concordant losses, via iterative regularization |
| n21-092 | [spotlight](https://openreview.net/forum?id=OItvP2-i9j) | [poster](https://openreview.net/forum?id=r6cNUjS8cm0) | 7.75 vs 6.25 | 4 + 4 | Closing the Gap: Tighter Analysis of Alternating Stochastic Gradient Methods for Bilevel Problems |
| n21-034 | [poster](https://openreview.net/forum?id=5ga5mfbGsRM) | [spotlight](https://openreview.net/forum?id=Xhj3PdCf4q9) | 6.00 vs 6.33 | 3 + 3 | Clustering Effect of Adversarial Robust Models |
| n21-219 | [spotlight](https://openreview.net/forum?id=Ra-2OvXr7UU) | [poster](https://openreview.net/forum?id=wn79e85F42W) | 6.67 vs 6.25 | 3 + 4 | Differentially Private Stochastic Optimization: New Results in Convex and Non-Convex Settings |
| n21-298 | [poster](https://openreview.net/forum?id=l4DQWgjbZg) | [spotlight](https://openreview.net/forum?id=LzwfcoEiB5O) | 6.25 vs 7.25 | 4 + 4 | Forster Decomposition and Learning Halfspaces with Noise |
| n21-281 | [spotlight](https://openreview.net/forum?id=jNq-i1zd0t9) | [poster](https://openreview.net/forum?id=bXTxva_xx6r) | 6.67 vs 5.50 | 3 + 4 | Generalized Depthwise-Separable Convolutions for Adversarially Robust and Efficient Neural Networks |
| n21-172 | [spotlight](https://openreview.net/forum?id=RX6PrcpXP-) | [poster](https://openreview.net/forum?id=zcrC_XDUFd) | 7.00 vs 6.67 | 4 + 3 | Learning with Holographic Reduced Representations |
| n21-136 | [poster](https://openreview.net/forum?id=eW8HEhY9F7C) | [spotlight](https://openreview.net/forum?id=OJXadQoWoTU) | 7.00 vs 7.00 | 4 + 4 | Nearly-Tight and Oblivious Algorithms for Explainable Clustering |
| n21-178 | [spotlight](https://openreview.net/forum?id=LU687itn08w) | [poster](https://openreview.net/forum?id=w6iVxEdh6bi) | 7.75 vs 6.25 | 4 + 4 | Offline RL Without Off-Policy Evaluation |
| n21-258 | [poster](https://openreview.net/forum?id=WYrC0Aentah) | [spotlight](https://openreview.net/forum?id=TZPidZS3r_z) | 7.00 vs 7.00 | 4 + 3 | On the Power of Differentiable Learning versus PAC and SQ Learning |
| n21-104 | [spotlight](https://openreview.net/forum?id=0vaPiltED1N) | [poster](https://openreview.net/forum?id=pbfAgoc_l2w) | 7.50 vs 6.75 | 4 + 4 | Sequence-to-Sequence Learning with Latent Neural Grammars |
| n21-284 | [spotlight](https://openreview.net/forum?id=27qon5Ut4PSl) | [poster](https://openreview.net/forum?id=SvrYl-FDq2) | 7.00 vs 6.00 | 4 + 4 | Sliced Mutual Information: A Scalable Measure of Statistical Dependence |
| n21-156 | [poster](https://openreview.net/forum?id=ake1XpIrDKN) | [spotlight](https://openreview.net/forum?id=9PBxTCg0F6m) | 6.50 vs 7.25 | 4 + 4 | Variational Inference for Continuous-Time Switching Dynamical Systems |
| n21-185 | [reject](https://openreview.net/forum?id=zwkj1_pxFM) | [spotlight](https://openreview.net/forum?id=bo75bBsQzeZ) | 5.75 vs 6.80 | 4 + 5 | A nonparametric method for gradual change problems with statistical guarantees |
| n21-039 | [reject](https://openreview.net/forum?id=zAuDbrHC6fq) | [spotlight](https://openreview.net/forum?id=o4t543Oon5G) | 4.33 vs 8.00 | 3 + 3 | Aligned Structured Sparsity Learning for Efficient Image Super-Resolution |
| n21-033 | [spotlight](https://openreview.net/forum?id=yNzF41lHYV) | [reject](https://openreview.net/forum?id=6tM849_6RF9) | 7.00 vs 5.50 | 4 + 4 | Believe What You See: Implicit Constraint Approach for Offline Multi-Agent Reinforcement Learning |
| n21-141 | [reject](https://openreview.net/forum?id=79zWncwO2p) | [spotlight](https://openreview.net/forum?id=1Kof-nkmQB8) | 6.00 vs 7.25 | 3 + 4 | Collaborating with Humans without Human Data |
| n21-025 | [reject](https://openreview.net/forum?id=cqD6imhK1TX) | [spotlight](https://openreview.net/forum?id=wPA_5Wsjt8i) | 5.00 vs 7.00 | 4 + 4 | Conditional Generation Using Polynomial Expansions |
| n21-017 | [reject](https://openreview.net/forum?id=kLJjmSrRB3S) | [spotlight](https://openreview.net/forum?id=iX0TSH45eOd) | 5.00 vs 7.00 | 4 + 5 | Continuous vs. Discrete Optimization of Deep Neural Networks |
| n21-121 | [reject](https://openreview.net/forum?id=wDI6CNTR3yP) | [spotlight](https://openreview.net/forum?id=wD6GWHqLuhS) | 4.25 vs 6.75 | 4 + 4 | CorticalFlow: A Diffeomorphic Mesh Transformer Network for Cortical Surface Reconstruction |
| n21-212 | [reject](https://openreview.net/forum?id=tgdoUMqlwMv) | [spotlight](https://openreview.net/forum?id=jGqcfSqOUR0) | 5.67 vs 6.67 | 3 + 3 | Disrupting Deep Uncertainty Estimation Without Harming Accuracy |
| n21-220 | [spotlight](https://openreview.net/forum?id=R-616EWWKF5) | [reject](https://openreview.net/forum?id=Gl8FHfMVTZu) | 6.50 vs 5.25 | 4 + 4 | Do Vision Transformers See Like Convolutional Neural Networks? |
| n21-262 | [reject](https://openreview.net/forum?id=SCN8UaetXx) | [spotlight](https://openreview.net/forum?id=AJofO-OFT40) | 5.40 vs 5.75 | 5 + 4 | Efficient Training of Visual Transformers with Small Datasets |
| n21-197 | [spotlight](https://openreview.net/forum?id=uyKk_avJ-p4) | [reject](https://openreview.net/forum?id=P7GUAXxS3ym) | 7.00 vs 4.25 | 4 + 4 | Improving Coherence and Consistency in Neural Sequence Models with Dual-System, Neuro-Symbolic Reasoning |
| n21-255 | [spotlight](https://openreview.net/forum?id=ThbM9_6DNU) | [reject](https://openreview.net/forum?id=I2pS-Lg7Xl) | 7.25 vs 5.00 | 4 + 3 | Learning Disentangled Behavior Embeddings |
| n21-230 | [spotlight](https://openreview.net/forum?id=sri2nuQC4Y) | [reject](https://openreview.net/forum?id=oErdeq9ajjX) | 6.50 vs 4.33 | 4 + 3 | Learning Generalized Gumbel-max Causal Mechanisms |
| n21-128 | [spotlight](https://openreview.net/forum?id=gEGPcdiXbky) | [reject](https://openreview.net/forum?id=LMotP3zsq_d) | 6.75 vs 4.75 | 4 + 4 | Learning to Generate Visual Questions with Noisy Supervision |
| n21-302 | [spotlight](https://openreview.net/forum?id=ntAkYRaIfox) | [reject](https://openreview.net/forum?id=Rupt2o4Fu6J) | 7.00 vs 4.75 | 3 + 4 | Machine learning structure preserving brackets for forecasting irreversible processes |
| n21-065 | [spotlight](https://openreview.net/forum?id=GoWFBE2-aLt) | [reject](https://openreview.net/forum?id=_6j_jQiYB2c) | 7.50 vs 5.75 | 4 + 4 | Non-asymptotic convergence bounds for Wasserstein approximation using point clouds |
| n21-062 | [spotlight](https://openreview.net/forum?id=oumDUrf2dAB) | [reject](https://openreview.net/forum?id=YAv9enSDW-a) | 7.33 vs 5.75 | 3 + 4 | On the Value of Infinite Gradients in Variational Autoencoder Models |
| n21-248 | [reject](https://openreview.net/forum?id=rMm9d_aDtOa) | [spotlight](https://openreview.net/forum?id=1XxaUEa3Yz) | 5.00 vs 6.75 | 3 + 4 | Online Knapsack with Frequency Predictions |
| n21-096 | [reject](https://openreview.net/forum?id=QwNLVId9Df) | [spotlight](https://openreview.net/forum?id=43fmQ-db-yJ) | 4.80 vs 6.25 | 5 + 4 | Program Synthesis Guided Reinforcement Learning for Partially Observed Environments |
| n21-003 | [reject](https://openreview.net/forum?id=5-GXHFNbq_U) | [spotlight](https://openreview.net/forum?id=OkFPq7ZtsQ) | 5.25 vs 6.75 | 4 + 4 | Prototypical Cross-Attention Networks for Multiple Object Tracking and Segmentation |
| n21-053 | [reject](https://openreview.net/forum?id=MdS0CgsH6Lf) | [spotlight](https://openreview.net/forum?id=qdphcA9jEbJ) | 4.25 vs 6.50 | 4 + 4 | Recursive Bayesian Networks: Generalising and Unifying Probabilistic Context-Free Grammars and Dynamic Bayesian Networks |
| n21-295 | [reject](https://openreview.net/forum?id=DLKakJ2W-In) | [spotlight](https://openreview.net/forum?id=nwu1RUCkei4) | 6.00 vs 6.67 | 4 + 3 | Relational Self-Attention: What's Missing in Attention for Video Understanding |
| n21-245 | [reject](https://openreview.net/forum?id=Z9K7sds_-jC) | [spotlight](https://openreview.net/forum?id=AHFfYwM7WGP) | 4.75 vs 6.75 | 4 + 4 | Residual2Vec: Debiasing graph embedding with random graphs |
| n21-091 | [spotlight](https://openreview.net/forum?id=pBKOx_dxYAN) | [reject](https://openreview.net/forum?id=9xPJ7cZ4ntc) | 6.75 vs 4.50 | 4 + 4 | SNIPS: Solving Noisy Inverse Problems Stochastically |
| n21-210 | [reject](https://openreview.net/forum?id=W6e384Lkjbw) | [spotlight](https://openreview.net/forum?id=rDdb26AQ0SO) | 5.25 vs 7.25 | 4 + 4 | Stochastic Online Linear Regression: the Forward Algorithm to Replace Ridge |

50 pairs, 53 oral-or-spotlight recommendations (the report's 54 less the one fatal-flaw rejection).
