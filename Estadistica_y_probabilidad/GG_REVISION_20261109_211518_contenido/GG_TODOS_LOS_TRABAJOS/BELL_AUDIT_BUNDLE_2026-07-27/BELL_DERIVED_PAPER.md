# Observational Deformation in Bell-Type Controlled Systems

Objective:
Use Bell-type experiments as highly controlled observational filtering environments.

Core ideas:
- detector filtering
- post-selection
- conditioning
- observational deformation
- induced dependence

## Model and Audit Algorithm

### Operational model

Let \(U_t\) denote the underlying attempt stream, \(A_\lambda\) the acceptance rule with control parameter(s) \(\lambda\), \(O_t\) the accepted observational stream, and \(T(O)\) the final inferential statistic, such as CHSH. The observational pipeline is written as

\[
U_t \xrightarrow{A_\lambda} O_t \xrightarrow{T} S.
\]

The central question is not whether filtering exists, but whether the map \(A_\lambda\) induces a deformation strong enough to alter the inferential object in a materially relevant way. In this framework, induced dependence is present when the accepted observational state \(O_t\) acquires structural regularities, imbalances, or sensitivities that are not transparently inherited from the broader attempt stream \(U_t\), but arise through the conditioning pipeline itself.

### Audit algorithm

The audit is performed in four linked layers.

1. **Local sensitivity by Taylor expansion.**  
   For any continuous acceptance parameter \(\lambda\), define the reported statistic locally as \(S(\lambda)\). Around the nominal value \(\lambda_0\),
   \[
   S(\lambda)\approx S(\lambda_0)+S'(\lambda_0)(\lambda-\lambda_0)+\frac{1}{2}S''(\lambda_0)(\lambda-\lambda_0)^2+\cdots .
   \]
   The first derivative measures local fragility of the inferential result to small changes in the declared pipeline, while the second derivative measures local tuning or curvature. This stage asks whether the nominal setting lies in a broad stable region or near a sharply tuned extremum.

2. **Global uncertainty propagation by Monte Carlo.**  
   Introduce an uncertainty model over the acceptance pipeline and propagate it through \(A_\lambda\) to obtain an ensemble of accepted samples and final statistics. This stage quantifies whether the reported value is robust under plausible perturbations of thresholds, timing windows, detection events, or acceptance logic, or whether the conclusion survives only in a narrow subset of parameter space.

3. **Latent-drift estimation by Kalman filtering.**  
   If the accepted observations are temporally ordered, model a latent state \(x_t\) and an observable process \(y_t\) by
   \[
   x_{t+1}=Ax_t+w_t,\qquad y_t=Hx_t+v_t.
   \]
   Kalman filtering is then used to estimate whether a hidden, slowly varying state organizes the acceptance rate, the accepted sample, or the inferential statistic. This stage asks whether the observational deformation is static or temporally structured.

4. **Sequential complexity by Kolmogorov-style estimators.**  
   Evaluate whether the accepted sequence is unusually compressible or unusually structured relative to null sequences with matched marginal rates. This stage does not prove mechanism, but tests whether the observational pipeline produces an accepted sequence that is simpler, more regular, or more patterned than expected under basic null organization.

### Decision logic

The artifact claim is graded, not binary.

- **Weak result:** the final inference is conditioned on an explicitly filtered sample.
- **Intermediate result:** the final inference is materially sensitive to the declared acceptance rule.
- **Strong result:** local sensitivity, Monte Carlo fragility, latent temporal drift, and sequential-structure diagnostics jointly indicate that the reported statistic is largely organized by the acceptance pipeline rather than stably inherited from the broader attempt stream.

Under this algorithm, no single tool is decisive. Taylor addresses local tuning, Monte Carlo addresses global robustness, Kalman addresses hidden temporal structure, and Kolmogorov-style estimators address sequential regularity. Only their convergence would justify a strong artifact interpretation.

## Audit Subsection: Hensen et al. 2015 as a Controlled Conditioning Case

Hensen et al. (Nature 526, 682-686, published October 21, 2015; DOI: 10.1038/nature15759) provide a useful Bell-type benchmark for auditing observational deformation because the acceptance rule is explicit and built into the protocol. The experiment uses an event-ready scheme in which only trials heralded by a valid coincidence event at station C are admitted into the CHSH analysis. In the language of the present framework, this makes it possible to distinguish between a broader physical stream of attempted entanglement-generation events and the filtered observable sample on which the final inference is made.

This feature makes the paper valuable for the induced-dependence program, but only in a limited and technically honest sense. The article does show explicit conditioning: failed entanglement-distribution attempts are excluded before Bell-statistic evaluation, and the reported result is therefore a statement about an accepted observational subset rather than about all raw physical attempts taken indiscriminately. However, this does not by itself imply that the reported Bell violation is an artifact. The event-ready filter is not hidden or opportunistic post hoc selection; it is a declared part of the experimental design intended to avoid the standard fair-sampling loophole while preserving locality conditions.

Operationally, the audit target is therefore not "Bell violation equals spurious filtering," but the full transformation chain

raw attempts -> heralded event-ready trials -> accepted Bell sample -> CHSH statistic.

Under this reading, Hensen et al. 2015 support the following narrower claim: Bell-type experiments can serve as highly controlled laboratories for quantifying how predeclared acceptance rules reshape the observable sample and therefore the inferential object. They do not, on their own, support the stronger claim that the Bell violation disappears once conditioning is recognized. That stronger conclusion would require direct reanalysis of the published dataset and explicit comparison between the unfiltered attempt stream and the accepted event-ready sample.

The later additional analysis by Hensen et al. (arXiv:1603.05705, posted March 17, 2016; revised April 1, 2016) is relevant here because it addresses the observed distribution of settings choices and random-number-generator bias. That follow-up strengthens the experimental claim against simple objections based on obvious setting imbalance, but it also reinforces the methodological point central to this paper: once the observational pipeline is explicit, one can separately audit the physical setup, the selection rule, the accepted sample, and the final inferential statistic.
