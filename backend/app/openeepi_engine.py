from math import exp, log, sqrt, isfinite
import numpy as np
from scipy.stats import beta, chi2, fisher_exact, t, f, norm
Z95=1.959963984540054

def _ci(x,n,alpha=.05):
    if n<=0:return [None,None]
    lo=0.0 if x==0 else float(beta.ppf(alpha/2,x,n-x+1)); hi=1.0 if x==n else float(beta.ppf(1-alpha/2,x+1,n-x)); return [lo,hi]
def _num(v,name,integer=False,positive=False):
    try:x=float(v)
    except:raise ValueError(f'{name} must be numeric')
    if not isfinite(x) or x<0 or (positive and x<=0):raise ValueError(f'{name} is invalid')
    if integer and x!=int(x):raise ValueError(f'{name} must be a whole number')
    return int(x) if integer else x

def screening(a,b,c,d):
    tp,fp,fn,tn=[_num(v,k,True) for v,k in zip([a,b,c,d],['TP','FP','FN','TN'])]; total=tp+fp+fn+tn
    if total==0:raise ValueError('At least one observation is required')
    div=lambda x,y:x/y if y else None; sens=div(tp,tp+fn); spec=div(tn,tn+fp); ppv=div(tp,tp+fp); npv=div(tn,tn+fn); acc=(tp+tn)/total
    plr=sens/(1-spec) if sens is not None and spec is not None and spec<1 else None; nlr=(1-sens)/spec if sens is not None and spec not in (None,0) else None; dor=plr/nlr if plr not in (None,0) and nlr not in (None,0) else None
    return {'table':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'total':total},'sensitivity':sens,'sensitivity_95ci':_ci(tp,tp+fn),'specificity':spec,'specificity_95ci':_ci(tn,tn+fp),'ppv':ppv,'ppv_95ci':_ci(tp,tp+fp),'npv':npv,'npv_95ci':_ci(tn,tn+fn),'accuracy':acc,'accuracy_95ci':_ci(tp+tn,total),'positive_likelihood_ratio':plr,'negative_likelihood_ratio':nlr,'diagnostic_odds_ratio':dor,'youden_j':sens+spec-1 if sens is not None and spec is not None else None,'f1_score':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,'prevalence':div(tp+fn,total),'method':'Diagnostic 2x2; exact Clopper-Pearson CIs.'}
def proportion(x,n,confidence=95):
    x=_num(x,'Events',True);n=_num(n,'Total',True,True)
    if x>n:raise ValueError('Events cannot exceed total')
    p=x/n;z=float(norm.ppf(.5+confidence/200));den=1+z*z/n;ctr=(p+z*z/(2*n))/den;h=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return {'proportion':p,'percent':100*p,'wilson_ci':[max(0,ctr-h),min(1,ctr+h)],'exact_ci':_ci(x,n),'method':'Wilson and exact binomial intervals.'}
def two_by_two(a,b,c,d):
    a,b,c,d=[_num(v,k,True) for v,k in zip([a,b,c,d],'abcd')];r1=a+b;r2=c+d;col1=a+c;col2=b+d
    if min(r1,r2,col1,col2)==0:raise ValueError('Each margin must be positive')
    return {'risk_ratio':(a/r1)/(c/r2) if c else None,'odds_ratio':a*d/(b*c) if b*c else None,'risk_difference':a/r1-c/r2,'chi_square':((a*d-b*c)**2*(a+b+c+d))/(r1*r2*col1*col2),'fisher_two_sided':float(fisher_exact([[a,b],[c,d]]).pvalue)}
def dose_response(successes,totals):
    y=np.asarray(successes,float);n=np.asarray(totals,float)
    if len(y)!=len(n) or len(y)<2 or np.any(n<=0) or np.any(y<0)|np.any(y>n):raise ValueError('Invalid dose groups')
    p=y/n;s=np.arange(1,len(y)+1,dtype=float);X=np.column_stack([np.ones(len(s)),s]);W=np.diag(n);bh=np.linalg.inv(X.T@W@X)@(X.T@W@p);res=p-X@bh;s2=float((n*res**2).sum()/max(1,len(y)-2));se=sqrt(max(s2*np.linalg.inv(X.T@W@X)[1,1],0));z=bh[1]/se if se else None
    return {'trend_slope':float(bh[1]),'trend_se':se,'trend_p':float(2*norm.sf(abs(z))) if z is not None else None,'proportions':p.tolist(),'method':'Weighted linear trend across ordered dose groups.'}
def rc_table(observed):
    a=np.asarray(observed,float)
    if a.ndim!=2 or min(a.shape)<2 or np.any(a<0):raise ValueError('Provide a non-negative R x C table')
    rows=a.sum(1);cols=a.sum(0);expct=np.outer(rows,cols)/a.sum();chi=float(((a-expct)**2/np.where(expct>0,expct,1)).sum());df=(a.shape[0]-1)*(a.shape[1]-1)
    return {'chi_square':chi,'df':df,'p_value':float(chi2.sf(chi,df)),'expected':expct.tolist(),'method':'Pearson chi-square independence test.'}
def matched_case_control(b,c):
    b=_num(b,'b',True);c=_num(c,'c',True)
    if b+c==0:raise ValueError('Discordant pairs required')
    if not b or not c:return {'matched_odds_ratio':None,'ci95':[None,None],'p_value':None,'method':'One discordant cell is zero; ratio is undefined.'}
    o=c/b;se=sqrt(1/b+1/c);return {'matched_odds_ratio':o,'ci95':[exp(log(o)-Z95*se),exp(log(o)+Z95*se)],'p_value':float(2*norm.sf(abs(log(o)/se))),'method':'Matched-pair odds ratio.'}
def rate(events,person_time):
    e=_num(events,'Events',True);pt=_num(person_time,'Person-time',positive=True);r=e/pt
    return {'rate':r,'exact_poisson_ci':[0,float(-log(.05)/pt)] if e==0 else [float(.5*chi2.ppf(.025,2*e)/pt),float(.5*chi2.ppf(.975,2*(e+1))/pt))],'events':e,'person_time':pt}
def compare_rates(e1,pt1,e2,pt2):
    r1=rate(e1,pt1);r2=rate(e2,pt2);ratio=r1['rate']/r2['rate'] if r2['rate'] else None;se=sqrt(1/e1+1/e2) if e1 and e2 else None;z=log(ratio)/se if ratio and se else None
    return {'rate1':r1,'rate2':r2,'rate_ratio':ratio,'ci95':[exp(log(ratio)-Z95*se),exp(log(ratio)+Z95*se)] if ratio and se else [None,None],'p_value':float(2*norm.sf(abs(z))) if z is not None else None}
def mean_ci(mean,sd,n,confidence=95):
    m=float(mean);s=float(sd);n=int(n);crit=float(t.ppf(.5+confidence/200,n-1));se=s/sqrt(n);return {'mean':m,'se':se,'ci95':[m-crit*se,m+crit*se],'method':'Student t CI.'}
def median_ci(values):
    x=np.asarray(values,float);x=x[np.isfinite(x)]
    if len(x)<2:raise ValueError('At least two observations required')
    return {'n':len(x),'median':float(np.median(x)),'p5':float(np.percentile(x,5)),'p25':float(np.percentile(x,25)),'p75':float(np.percentile(x,75)),'p95':float(np.percentile(x,95)),'method':'Empirical percentile summary; exact legacy CI method requires source-specific validation.'}
def t_test(m1,sd1,n1,m2,sd2,n2):
    m1,s1,n1=float(m1),float(sd1),int(n1);m2,s2,n2=float(m2),float(sd2),int(n2);se=sqrt(s1*s1/n1+s2*s2/n2);diff=m1-m2;df=(s1*s1/n1+s2*s2/n2)**2/((s1*s1/n1)**2/(n1-1)+(s2*s2/n2)**2/(n2-1));tv=diff/se;return {'mean_difference':diff,'t':tv,'df':df,'p_value':float(2*t.sf(abs(tv),df)),'ci95':[diff-Z95*se,diff+Z95*se],'method':'Welch independent-samples t test.'}
def anova(groups):
    g=[np.asarray(x,float) for x in groups];k=len(g);n=sum(len(x) for x in g);grand=np.concatenate(g).mean();ssb=sum(len(x)*(x.mean()-grand)**2 for x in g);ssw=sum(((x-x.mean())**2).sum() for x in g);dfb=k-1;dfw=n-k;Fv=(ssb/dfb)/(ssw/dfw);return {'F':Fv,'df_between':dfb,'df_within':dfw,'p_value':float(f.sf(Fv,dfb,dfw)),'method':'One-way ANOVA.'}
def sample_size_proportion(p,margin,confidence=95):
    p=float(p);d=float(margin);z=float(norm.ppf(.5+confidence/200));return {'sample_size':int(np.ceil(z*z*p*(1-p)/(d*d))),'formula':'z²p(1-p)/d²'}
def sample_size_mean(sd,diff,confidence=95,power=80):
    z1=float(norm.ppf(.5+confidence/200));z2=float(norm.ppf(power/100));n=2*((z1+z2)*float(sd)/float(diff))**2;return {'sample_size_per_group':int(np.ceil(n)),'total_sample_size':int(np.ceil(2*n)),'formula':'Two independent means normal approximation.'}
def sample_size_cc(p0,or_value,ratio=1,alpha=.05,power=.8):
    p0=float(p0);OR=float(or_value);r=float(ratio);p1=OR*p0/(1-p0+OR*p0);z1=float(norm.ppf(1-alpha/2));z2=float(norm.ppf(power));q0=1-p0;q1=1-p1;n=((z1*sqrt((1+1/r)*p0*q0)+z2*sqrt(p0*q0+p1*q1/r))/(p1-p0))**2;return {'cases':int(np.ceil(n)),'controls':int(np.ceil(n*r)),'p_case':p1,'formula':'Normal approximation for two independent proportions.'}
def sample_size_two_prop(p1,p0,ratio=1,confidence=95,power=80):
    p1=float(p1);p0=float(p0);r=float(ratio);z1=float(norm.ppf(.5+confidence/200));z2=float(norm.ppf(power/100));n=((z1*sqrt(p1*(1-p1)+p0*(1-p0)/r)+z2*sqrt(p1*(1-p1)+p0*(1-p0)/r))/(p1-p0))**2;return {'group1':int(np.ceil(n)),'group2':int(np.ceil(n*r)),'total':int(np.ceil(n*(1+r))),'formula':'Two-proportion normal approximation.'}
def power_proportion(n,p,p0,alpha=.05):
    n=int(n);p=float(p);p0=float(p0);se=sqrt(p*(1-p)/n);z=abs(p-p0)/se;za=float(norm.ppf(1-alpha/2));pw=float(norm.cdf(-za+z)+1-norm.cdf(za+z));return {'power':pw,'power_percent':100*pw}
def power_two_prop(n1,n2,p1,p0,alpha=.05):
    p1=float(p1);p0=float(p0);se=sqrt(p1*(1-p1)/n1+p0*(1-p0)/n2);z=abs(p1-p0)/se;za=float(norm.ppf(1-alpha/2));pw=float(norm.cdf(-za+z)+1-norm.cdf(za+z));return {'power':pw,'power_percent':100*pw,'method':'Normal approximation for two independent proportions.'}
def power_mean(n1,n2,sd,diff,alpha=.05):
    se=float(sd)*sqrt(1/n1+1/n2);z=abs(float(diff))/se;za=float(norm.ppf(1-alpha/2));pw=float(norm.cdf(-za+z)+1-norm.cdf(za+z));return {'power':pw,'power_percent':100*pw,'method':'Normal approximation for two independent means.'}
def random_numbers(n,low,high,seed=None):
    return {'numbers':np.random.default_rng(None if seed is None else int(seed)).integers(int(low),int(high)+1,int(n)).tolist()}
def calculate(module,d):
    if module=='smr':
        o=_num(d['observed'],'Observed',True);e=_num(d['expected'],'Expected',positive=True);s=o/e;se=sqrt(o)/e if o else 0;return {'smr':s,'ci95':[max(0,s-Z95*se),s+Z95*se]}
    if module=='proportion':return proportion(d['x'],d['n'],d.get('confidence',95))
    if module=='two':return two_by_two(d['a'],d['b'],d['c'],d['d'])
    if module=='dose':return dose_response(d['successes'],d['totals'])
    if module=='rc':return rc_table(d['observed'])
    if module=='match':return matched_case_control(d['b'],d['c'])
    if module=='screening':return screening(d['tp'],d['fp'],d['fn'],d['tn'])
    if module=='rate':return rate(d['events'],d['person_time'])
    if module=='compare_rates':return compare_rates(d['e1'],d['pt1'],d['e2'],d['pt2'])
    if module=='mean':return mean_ci(d['mean'],d['sd'],d['n'],d.get('confidence',95))
    if module=='median':return median_ci(d['values'])
    if module=='ttest':return t_test(d['m1'],d['sd1'],d['n1'],d['m2'],d['sd2'],d['n2'])
    if module=='anova':return anova(d['groups'])
    if module=='ss_proportion':return sample_size_proportion(d['p'],d['margin'],d.get('confidence',95))
    if module=='ss_cc':return sample_size_cc(d['p0'],d['or'],d.get('ratio',1))
    if module in ('ss_cohort','ss_rct'):return sample_size_two_prop(d.get('p1',.3),d.get('p0',.15),d.get('ratio',1),d.get('confidence',95),d.get('power',80))
    if module=='ss_mean':return sample_size_mean(d['sd'],d['diff'],d.get('confidence',95),d.get('power',80))
    if module=='power_proportion':return power_proportion(d['n'],d['p'],d['p0'])
    if module in ('power_cc','power_cohort','power_rct'):return power_two_prop(d.get('n_cases',d.get('n_exposed',d.get('n1',100))),d.get('n_controls',d.get('n_unexposed',d.get('n2',100))),d.get('p_cases',d.get('risk_exposed',d.get('p1',.3))),d.get('p_controls',d.get('risk_unexposed',d.get('p2',.15))))
    if module=='power_mean':return power_mean(d.get('n1',100),d.get('n2',100),d.get('sd',10),d.get('diff',5))
    if module=='random':return random_numbers(d['n'],d['low'],d['high'],d.get('seed'))
    raise ValueError(f'Calculator module not implemented: {module}')
