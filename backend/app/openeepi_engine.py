from math import exp, log, sqrt, isfinite, erf
import numpy as np
from scipy.stats import beta, chi2, fisher_exact, t, f, norm

Z95 = 1.959963984540054


def _ci(x, n, alpha=0.05):
    if n <= 0: return [None, None]
    x = int(x); n = int(n)
    lo = 0.0 if x == 0 else float(beta.ppf(alpha/2, x, n-x+1))
    hi = 1.0 if x == n else float(beta.ppf(1-alpha/2, x+1, n-x))
    return [lo, hi]


def _num(v, name, integer=False, positive=False):
    try: x = float(v)
    except Exception: raise ValueError(f'{name} must be numeric')
    if not isfinite(x) or (positive and x <= 0) or (not positive and x < 0): raise ValueError(f'{name} is invalid')
    if integer and x != int(x): raise ValueError(f'{name} must be a whole number')
    return int(x) if integer else x


def screening(a,b,c,d):
    tp,fp,fn,tn=[_num(v,k,True) for v,k in zip([a,b,c,d],['TP','FP','FN','TN'])]
    total=tp+fp+fn+tn
    if total==0: raise ValueError('At least one observation is required')
    div=lambda x,y: x/y if y else None
    sens=div(tp,tp+fn); spec=div(tn,tn+fp); ppv=div(tp,tp+fp); npv=div(tn,tn+fn); acc=(tp+tn)/total
    plr=sens/(1-spec) if sens is not None and spec is not None and spec<1 else None
    nlr=(1-sens)/spec if sens is not None and spec not in (None,0) else None
    dor=plr/nlr if plr not in (None,0) and nlr not in (None,0) else None
    return {'table':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'total':total},'sensitivity':sens,'sensitivity_95ci':_ci(tp,tp+fn),'specificity':spec,'specificity_95ci':_ci(tn,tn+fp),'ppv':ppv,'ppv_95ci':_ci(tp,tp+fp),'npv':npv,'npv_95ci':_ci(tn,tn+fn),'accuracy':acc,'accuracy_95ci':_ci(tp+tn,total),'positive_likelihood_ratio':plr,'negative_likelihood_ratio':nlr,'diagnostic_odds_ratio':dor,'youden_j':(sens+spec-1) if sens is not None and spec is not None else None,'f1_score':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,'prevalence':div(tp+fn,total),'method':'Diagnostic 2x2 table; exact Clopper-Pearson 95% CIs.'}


def proportion(x,n,confidence=95):
    x=_num(x,'Events',True); n=_num(n,'Total',True,True)
    if x>n: raise ValueError('Events cannot exceed total')
    p=x/n; z=float(norm.ppf(0.5+confidence/200)); den=1+z*z/n; ctr=(p+z*z/(2*n))/den; half=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return {'x':x,'n':n,'proportion':p,'percent':100*p,'wilson_ci':[max(0,ctr-half),min(1,ctr+half)],'exact_ci':_ci(x,n),'method':'Wilson score interval and exact Clopper-Pearson interval.'}


def two_by_two(a,b,c,d):
    a,b,c,d=[_num(v,k,True) for v,k in zip([a,b,c,d],'abcd')]
    r1=a+b; r2=c+d; col1=a+c; col2=b+d
    if min(r1,r2,col1,col2)==0: raise ValueError('Each margin required for risk/odds measures')
    rr=(a/r1)/(c/r2) if c else None; orr=(a*d)/(b*c) if b*c else None; rd=a/r1-c/r2
    return {'table':[[a,b],[c,d]],'risk_ratio':rr,'odds_ratio':orr,'risk_difference':rd,'risk_a':a/r1,'risk_b':c/r2,'chi_square':((a*d-b*c)**2*(a+b+c+d))/(r1*r2*col1*col2),'fisher_two_sided':float(fisher_exact([[a,b],[c,d]],alternative='two-sided').pvalue)}


def dose_response(successes, totals):
    y=np.asarray(successes,dtype=float); n=np.asarray(totals,dtype=float)
    if len(y)!=len(n) or len(y)<2 or np.any(n<=0) or np.any(y<0) or np.any(y>n): raise ValueError('Provide at least two dose groups with valid cases and totals')
    p=y/n; scores=np.arange(1,len(y)+1,dtype=float); w=n
    X=np.column_stack([np.ones(len(scores)),scores]); W=np.diag(w); beta_hat=np.linalg.inv(X.T@W@X)@(X.T@W@p); resid=p-X@beta_hat; s2=float((w*resid**2).sum()/max(1,len(y)-2)); se=sqrt(max(s2*np.linalg.inv(X.T@W@X)[1,1],0)); z=beta_hat[1]/se if se else None; pval=float(2*norm.sf(abs(z))) if z is not None else None
    return {'groups':len(y),'trend_slope':float(beta_hat[1]),'trend_se':se,'trend_z':z,'trend_p':pval,'proportions':p.tolist(),'method':'Weighted linear trend of group proportions using ordered dose scores.'}


def rc_table(observed):
    a=np.asarray(observed,dtype=float)
    if a.ndim!=2 or min(a.shape)<2 or np.any(a<0): raise ValueError('Provide a non-negative R x C table')
    total=a.sum(); rows=a.sum(axis=1); cols=a.sum(axis=0); expected=np.outer(rows,cols)/total
    chi=float(((a-expected)**2/np.where(expected>0,expected,1)).sum()); df=(a.shape[0]-1)*(a.shape[1]-1); p=float(chi2.sf(chi,df))
    return {'rows':int(a.shape[0]),'columns':int(a.shape[1]),'chi_square':chi,'df':df,'p_value':p,'expected':expected.tolist(),'method':'Pearson chi-square test of independence.'}


def matched_case_control(b,c):
    b=_num(b,'Discordant exposed controls',True); c=_num(c,'Discordant exposed cases',True)
    if b+c==0: raise ValueError('At least one discordant pair is required')
    orr=c/b if b else None; se=sqrt(1/b+1/c) if b and c else None; ci=[exp(log(orr)-Z95*se),exp(log(orr)+Z95*se)] if se else [None,None]; p=float(2*norm.sf(abs(log(orr)/se))) if se else None
    return {'matched_odds_ratio':orr,'ci95':ci,'p_value':p,'discordant_pairs':b+c,'method':'Matched-pair odds ratio based on discordant pairs.'}


def rate(events,person_time):
    e=_num(events,'Events',True); pt=_num(person_time,'Person-time',positive=True); r=e/pt; ci=[0,0]
    if e>0:
        lo=0.5*chi2.ppf(.025,2*e)/pt; hi=0.5*chi2.ppf(.975,2*(e+1))/pt; ci=[float(lo),float(hi)]
    else: ci=[0,float(-log(.05)/pt)]
    return {'events':e,'person_time':pt,'rate':r,'rate_per_unit':r,'exact_poisson_ci':ci}


def compare_rates(e1,pt1,e2,pt2):
    r1=rate(e1,pt1); r2=rate(e2,pt2); ratio=r1['rate']/r2['rate'] if r2['rate'] else None; se=sqrt(1/e1+1/e2) if e1 and e2 else None; ci=[exp(log(ratio)-Z95*se),exp(log(ratio)+Z95*se)] if se and ratio else [None,None]; z=log(ratio)/se if se and ratio else None
    return {'rate1':r1,'rate2':r2,'rate_ratio':ratio,'ci95':ci,'z':z,'p_value':float(2*norm.sf(abs(z))) if z is not None else None}


def mean_ci(mean,sd,n,confidence=95):
    m=_num(mean,'Mean'); s=_num(sd,'SD'); n=_num(n,'N',True,True); alpha=1-confidence/100; crit=float(t.ppf(1-alpha/2,n-1)); se=s/sqrt(n)
    return {'mean':m,'sd':s,'n':n,'se':se,'ci95':[m-crit*se,m+crit*se],'method':'Student t confidence interval for one mean.'}


def median_ci(values):
    x=np.sort(np.asarray(values,dtype=float)); n=len(x)
    if n<2: raise ValueError('At least two observations required')
    med=float(np.median(x)); return {'n':n,'median':med,'q1':float(np.percentile(x,25)),'q3':float(np.percentile(x,75)),'percentiles':{'p5':float(np.percentile(x,5)),'p25':float(np.percentile(x,25)),'p50':med,'p75':float(np.percentile(x,75)),'p95':float(np.percentile(x,95))},'method':'Empirical percentile summary; bootstrap CI should be used for publication-grade median inference.'}


def t_test(m1,sd1,n1,m2,sd2,n2,paired=False):
    m1,sd1,n1=float(m1),float(sd1),int(n1); m2,sd2,n2=float(m2),float(sd2),int(n2)
    if min(n1,n2)<=1 or min(sd1,sd2)<0: raise ValueError('Invalid group inputs')
    se=sqrt(sd1**2/n1+sd2**2/n2); diff=m1-m2; df=(sd1**2/n1+sd2**2/n2)**2/((sd1**2/n1)**2/(n1-1)+(sd2**2/n2)**2/(n2-1)); tv=diff/se if se else None; p=float(2*t.sf(abs(tv),df)) if tv is not None else None
    return {'mean_difference':diff,'se':se,'t':tv,'df':df,'p_value':p,'ci95':[diff-Z95*se,diff+Z95*se],'method':'Welch two-sample t test (independent groups).'}


def anova(groups):
    arr=[np.asarray(g,dtype=float) for g in groups]; arr=[g[np.isfinite(g)] for g in arr]; k=len(arr); n=sum(len(g) for g in arr)
    if k<2 or any(len(g)<2 for g in arr): raise ValueError('At least two groups with two observations each required')
    grand=np.concatenate(arr).mean(); ssb=sum(len(g)*(g.mean()-grand)**2 for g in arr); ssw=sum(((g-g.mean())**2).sum() for g in arr); dfb=k-1; dfw=n-k; Fv=(ssb/dfb)/(ssw/dfw) if ssw else None; p=float(f.sf(Fv,dfb,dfw)) if Fv is not None else None
    return {'groups':k,'n':n,'ss_between':float(ssb),'ss_within':float(ssw),'df_between':dfb,'df_within':dfw,'F':Fv,'p_value':p,'method':'One-way ANOVA.'}


def _z(conf): return float(norm.ppf(0.5+conf/200))

def sample_size_proportion(p,margin,confidence=95):
    p=float(p); margin=float(margin); z=_z(confidence)
    if not 0<p<1 or margin<=0: raise ValueError('p must be 0-1 and margin > 0')
    return {'sample_size':int(np.ceil(z*z*p*(1-p)/(margin*margin))),'formula':'n = z² p(1-p) / d²'}


def sample_size_mean(sd,diff,confidence=95,power=80):
    z1=_z(confidence); z2=float(norm.ppf(power/100)); n=2*((z1+z2)*float(sd)/float(diff))**2
    return {'sample_size_per_group':int(np.ceil(n)),'total_sample_size':int(np.ceil(2*n)),'formula':'two independent means normal approximation'}


def sample_size_cc(p0,or_value,ratio=1,alpha=0.05,power=.80):
    p0=float(p0); OR=float(or_value); r=float(ratio); z1=float(norm.ppf(1-alpha/2)); z2=float(norm.ppf(power)); p1=OR*p0/(1-p0+OR*p0); q0=1-p0; q1=1-p1
    n_case=((z1*sqrt((1+1/r)*((p0*q0)+(p1*q1)/r))+z2*sqrt(p0*q0+p1*q1/r))**2)/((p1-p0)**2)
    return {'cases':int(np.ceil(n_case)),'controls':int(np.ceil(n_case*r)),'p_control':p0,'p_case':p1}


def power_proportion(n,p,p0,alpha=.05):
    se=sqrt(p*(1-p)/n); z=abs(p-p0)/se; power=float(norm.cdf(-_z(95)+z)+1-norm.cdf(_z(95)+z)); return {'power':power,'power_percent':100*power,'z_effect':z}


def random_numbers(n,low,high,seed=None):
    rng=np.random.default_rng(seed); return {'numbers':rng.integers(int(low),int(high)+1,int(n)).tolist()}


def calculate(module, data):
    if module=='smr':
        observed=_num(data['observed'],'Observed',True); expected=_num(data['expected'],'Expected',positive=True); smr=observed/expected; se=sqrt(observed)/expected if observed else 0; return {'observed':observed,'expected':expected,'smr':smr,'ci95':[max(0,smr-Z95*se),smr+Z95*se]}
    if module=='proportion': return proportion(data['x'],data['n'],data.get('confidence',95))
    if module=='two_by_two': return two_by_two(data['a'],data['b'],data['c'],data['d'])
    if module=='dose_response': return dose_response(data['successes'],data['totals'])
    if module=='rc': return rc_table(data['observed'])
    if module=='matched_cc': return matched_case_control(data['b'],data['c'])
    if module=='screening': return screening(data['tp'],data['fp'],data['fn'],data['tn'])
    if module=='rate': return rate(data['events'],data['person_time'])
    if module=='compare_rates': return compare_rates(data['e1'],data['pt1'],data['e2'],data['pt2'])
    if module=='mean_ci': return mean_ci(data['mean'],data['sd'],data['n'],data.get('confidence',95))
    if module=='median': return median_ci(data['values'])
    if module=='ttest': return t_test(data['m1'],data['sd1'],data['n1'],data['m2'],data['sd2'],data['n2'])
    if module=='anova': return anova(data['groups'])
    if module=='ss_proportion': return sample_size_proportion(data['p'],data['margin'],data.get('confidence',95))
    if module=='ss_cc': return sample_size_cc(data['p0'],data['or'],data.get('ratio',1),data.get('alpha',.05),data.get('power',.80))
    if module=='ss_mean': return sample_size_mean(data['sd'],data['diff'],data.get('confidence',95),data.get('power',80))
    if module=='power_proportion': return power_proportion(data['n'],data['p'],data['p0'],data.get('alpha',.05))
    if module=='random': return random_numbers(data['n'],data['low'],data['high'],data.get('seed'))
    if module=='settings': return {'confidence_options':[90,95,99],'default_confidence':95,'tail':'two-sided'}
    raise ValueError(f'Calculator module not implemented: {module}')
