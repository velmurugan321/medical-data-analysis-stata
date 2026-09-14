from math import exp, log, sqrt, isfinite
import numpy as np
from scipy.stats import beta, chi2, fisher_exact, t, f, norm
Z=1.959963984540054

def ci(x,n):
    if n<=0:return [None,None]
    return [0.0 if x==0 else float(beta.ppf(.025,x,n-x+1)),1.0 if x==n else float(beta.ppf(.975,x+1,n-x))]
def whole(x,name):
    try:v=float(x)
    except:raise ValueError(f'{name} must be numeric')
    if not isfinite(v) or v<0 or v!=int(v):raise ValueError(f'{name} must be a non-negative whole number')
    return int(v)
def screening(tp,fp,fn,tn):
    tp,fp,fn,tn=[whole(x,n) for x,n in zip([tp,fp,fn,tn],['TP','FP','FN','TN'])];N=tp+fp+fn+tn
    if N==0:raise ValueError('At least one observation is required')
    q=lambda a,b:a/b if b else None;s=q(tp,tp+fn);sp=q(tn,tn+fp);ppv=q(tp,tp+fp);npv=q(tn,tn+fn);acc=(tp+tn)/N
    plr=s/(1-sp) if s is not None and sp is not None and sp<1 else None;nlr=(1-s)/sp if s is not None and sp else None
    return {'table':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'total':N},'sensitivity':s,'sensitivity_95ci':ci(tp,tp+fn),'specificity':sp,'specificity_95ci':ci(tn,tn+fp),'ppv':ppv,'ppv_95ci':ci(tp,tp+fp),'npv':npv,'npv_95ci':ci(tn,tn+fn),'accuracy':acc,'accuracy_95ci':ci(tp+tn,N),'positive_likelihood_ratio':plr,'negative_likelihood_ratio':nlr,'diagnostic_odds_ratio':plr/nlr if plr and nlr else None,'youden_j':s+sp-1 if s is not None and sp is not None else None,'f1_score':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,'prevalence':q(tp+fn,N),'method':'Diagnostic 2x2 with exact Clopper-Pearson 95% CIs.'}
def proportion(x,n,confidence=95):
    x=whole(x,'Events');n=whole(n,'Total')
    if n==0 or x>n:raise ValueError('0 <= Events <= Total and Total > 0 required')
    p=x/n;z=float(norm.ppf(.5+float(confidence)/200));den=1+z*z/n;ctr=(p+z*z/(2*n))/den;h=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return {'proportion':p,'percent':100*p,'wilson_ci':[max(0,ctr-h),min(1,ctr+h)],'exact_ci':ci(x,n),'method':'Wilson score and exact binomial intervals.'}
def two(a,b,c,d):
    a,b,c,d=[whole(x,k) for x,k in zip([a,b,c,d],'abcd')];r1=a+b;r2=c+d;c1=a+c;c2=b+d
    if min(r1,r2,c1,c2)==0:raise ValueError('All margins must be positive')
    return {'risk_ratio':(a/r1)/(c/r2) if c else None,'odds_ratio':a*d/(b*c) if b*c else None,'risk_difference':a/r1-c/r2,'chi_square':((a*d-b*c)**2*(a+b+c+d))/(r1*r2*c1*c2),'fisher_two_sided':float(fisher_exact([[a,b],[c,d]]).pvalue)}
def dose(successes,totals):
    y=np.asarray(successes,float);n=np.asarray(totals,float)
    if len(y)!=len(n) or len(y)<2 or np.any(n<=0) or np.any(y<0) or np.any(y>n):raise ValueError('Invalid dose arrays')
    p=y/n;s=np.arange(1,len(y)+1,dtype=float);X=np.c_[np.ones(len(s)),s];W=np.diag(n);bh=np.linalg.inv(X.T@W@X)@(X.T@W@p);res=p-X@bh;se=sqrt(max(float((n*res**2).sum()/max(1,len(y)-2))*np.linalg.inv(X.T@W@X)[1,1],0));z=bh[1]/se if se else None
    return {'trend_slope':float(bh[1]),'trend_se':se,'trend_p':float(2*norm.sf(abs(z))) if z is not None else None,'proportions':p.tolist(),'method':'Weighted linear trend using ordered dose scores.'}
def rc(obs):
    a=np.asarray(obs,float)
    if a.ndim!=2 or min(a.shape)<2 or np.any(a<0):raise ValueError('R x C matrix required')
    ex=np.outer(a.sum(1),a.sum(0))/a.sum();x=float(((a-ex)**2/np.where(ex>0,ex,1)).sum());df=(a.shape[0]-1)*(a.shape[1]-1)
    return {'chi_square':x,'df':df,'p_value':float(chi2.sf(x,df)),'expected':ex.tolist(),'method':'Pearson chi-square independence test.'}
def match(b,c):
    b=whole(b,'b');c=whole(c,'c')
    if not b or not c:return {'matched_odds_ratio':None,'ci95':[None,None],'p_value':None,'method':'Odds ratio undefined when a discordant cell is zero.'}
    o=c/b;se=sqrt(1/b+1/c);return {'matched_odds_ratio':o,'ci95':[exp(log(o)-Z*se),exp(log(o)+Z*se)],'p_value':float(2*norm.sf(abs(log(o)/se))),'method':'Matched-pair odds ratio.'}
def rate(e,pt):
    e=whole(e,'Events');pt=float(pt)
    if pt<=0:raise ValueError('Person-time must be > 0')
    r=e/pt;lo=0 if e==0 else .5*chi2.ppf(.025,2*e)/pt;hi=-log(.05)/pt if e==0 else .5*chi2.ppf(.975,2*(e+1))/pt
    return {'rate':r,'exact_poisson_ci':[float(lo),float(hi)],'events':e,'person_time':pt}
def compare_rates(e1,pt1,e2,pt2):
    r1=rate(e1,pt1);r2=rate(e2,pt2)
    if not r2['rate'] or not e1 or not e2:return {'rate1':r1,'rate2':r2,'rate_ratio':None,'ci95':[None,None],'p_value':None}
    rr=r1['rate']/r2['rate'];se=sqrt(1/e1+1/e2);z=log(rr)/se
    return {'rate1':r1,'rate2':r2,'rate_ratio':rr,'ci95':[exp(log(rr)-Z*se),exp(log(rr)+Z*se)],'p_value':float(2*norm.sf(abs(z)))}
def mean_ci(m,sd,n,confidence=95):
    m=float(m);sd=float(sd);n=int(n)
    if n<2 or sd<0:raise ValueError('N >= 2 and SD >= 0 required')
    crit=float(t.ppf(.5+float(confidence)/200,n-1));se=sd/sqrt(n);return {'mean':m,'se':se,'ci95':[m-crit*se,m+crit*se],'method':'Student t CI.'}
def median(values):
    x=np.asarray(values,float);x=x[np.isfinite(x)]
    if len(x)<2:raise ValueError('At least two observations required')
    return {'n':len(x),'median':float(np.median(x)),'p5':float(np.percentile(x,5)),'p25':float(np.percentile(x,25)),'p75':float(np.percentile(x,75)),'p95':float(np.percentile(x,95)),'method':'Empirical percentiles; legacy exact median CI requires source-specific validation.'}
def ttest(m1,sd1,n1,m2,sd2,n2):
    m1,sd1,n1=float(m1),float(sd1),int(n1);m2,sd2,n2=float(m2),float(sd2),int(n2);se=sqrt(sd1**2/n1+sd2**2/n2);df=(sd1**2/n1+sd2**2/n2)**2/((sd1**2/n1)**2/(n1-1)+(sd2**2/n2)**2/(n2-1));tv=(m1-m2)/se
    return {'mean_difference':m1-m2,'t':tv,'df':df,'p_value':float(2*t.sf(abs(tv),df)),'ci95':[m1-m2-Z*se,m1-m2+Z*se],'method':'Welch independent-samples t test.'}
def anova(groups):
    g=[np.asarray(x,float) for x in groups];k=len(g);n=sum(len(x) for x in g);allx=np.concatenate(g);gm=allx.mean();ssb=sum(len(x)*(x.mean()-gm)**2 for x in g);ssw=sum(((x-x.mean())**2).sum() for x in g);df1=k-1;df2=n-k;Fv=(ssb/df1)/(ssw/df2)
    return {'F':Fv,'df_between':df1,'df_within':df2,'p_value':float(f.sf(Fv,df1,df2)),'method':'One-way ANOVA.'}
def ss_prop(p,d,confidence=95):
    p=float(p);d=float(d);z=float(norm.ppf(.5+float(confidence)/200));return {'sample_size':int(np.ceil(z*z*p*(1-p)/(d*d))),'formula':'z²p(1-p)/d²'}
def ss_two(p1,p0,ratio=1,confidence=95,power=80):
    p1,p0,r=float(p1),float(p0),float(ratio);z1=float(norm.ppf(.5+float(confidence)/200));z2=float(norm.ppf(float(power)/100));n=((z1*sqrt(p1*(1-p1)+p0*(1-p0)/r)+z2*sqrt(p1*(1-p1)+p0*(1-p0)/r))/(p1-p0))**2
    return {'group1':int(np.ceil(n)),'group2':int(np.ceil(n*r)),'total':int(np.ceil(n*(1+r))),'method':'Normal approximation for two independent proportions.'}
def ss_cc(p0,odds,ratio=1):
    p0=float(p0);odds=float(odds);p1=odds*p0/(1-p0+odds*p0);return ss_two(p1,p0,ratio)
def ss_mean(sd,diff,confidence=95,power=80):
    z1=float(norm.ppf(.5+float(confidence)/200));z2=float(norm.ppf(float(power)/100));n=2*((z1+z2)*float(sd)/float(diff))**2;return {'sample_size_per_group':int(np.ceil(n)),'total_sample_size':int(np.ceil(2*n)),'method':'Normal approximation for two means.'}
def power_prop(n,p,p0):
    n=int(n);se=sqrt(float(p)*(1-float(p))/n);z=abs(float(p)-float(p0))/se;za=Z;pw=norm.cdf(-za+z)+1-norm.cdf(za+z);return {'power':float(pw),'power_percent':float(100*pw)}
def power_two(n1,n2,p1,p0):
    se=sqrt(float(p1)*(1-float(p1))/int(n1)+float(p0)*(1-float(p0))/int(n2));z=abs(float(p1)-float(p0))/se;pw=norm.cdf(-Z+z)+1-norm.cdf(Z+z);return {'power':float(pw),'power_percent':float(100*pw),'method':'Normal approximation for two independent proportions.'}
def power_mean(n1,n2,sd,diff):
    se=float(sd)*sqrt(1/int(n1)+1/int(n2));z=abs(float(diff))/se;pw=norm.cdf(-Z+z)+1-norm.cdf(Z+z);return {'power':float(pw),'power_percent':float(100*pw),'method':'Normal approximation for two means.'}
def random_numbers(n,low,high,seed=None):return {'numbers':np.random.default_rng(None if seed in (None,'') else int(seed)).integers(int(low),int(high)+1,int(n)).tolist()}
def calculate(m,d):
    if m=='smr':
        o=whole(d['observed'],'Observed');e=float(d['expected']);s=o/e;se=sqrt(o)/e if o else 0;return {'smr':s,'ci95':[max(0,s-Z*se),s+Z*se]}
    if m=='proportion':return proportion(d['x'],d['n'],d.get('confidence',95))
    if m=='two':return two(d['a'],d['b'],d['c'],d['d'])
    if m=='dose':return dose(d['successes'],d['totals'])
    if m=='rc':return rc(d['observed'])
    if m=='match':return match(d['b'],d['c'])
    if m=='screening':return screening(d['tp'],d['fp'],d['fn'],d['tn'])
    if m=='rate':return rate(d['events'],d['person_time'])
    if m=='compare_rates':return compare_rates(d['e1'],d['pt1'],d['e2'],d['pt2'])
    if m=='mean':return mean_ci(d['mean'],d['sd'],d['n'],d.get('confidence',95))
    if m=='median':return median(d['values'])
    if m=='ttest':return ttest(d['m1'],d['sd1'],d['n1'],d['m2'],d['sd2'],d['n2'])
    if m=='anova':return anova(d['groups'])
    if m=='ss_proportion':return ss_prop(d['p'],d['margin'],d.get('confidence',95))
    if m=='ss_cc':return ss_cc(d['p0'],d['or'],d.get('ratio',1))
    if m in ('ss_cohort','ss_rct'):return ss_two(d.get('p1',.3),d.get('p0',.15),d.get('ratio',1),d.get('confidence',95),d.get('power',80))
    if m=='ss_mean':return ss_mean(d['sd'],d['diff'],d.get('confidence',95),d.get('power',80))
    if m=='power_proportion':return power_prop(d['n'],d['p'],d['p0'])
    if m in ('power_cc','power_cohort','power_rct'):return power_two(d.get('n_cases',d.get('n_exposed',d.get('n1',100))),d.get('n_controls',d.get('n_unexposed',d.get('n2',100))),d.get('p_cases',d.get('risk_exposed',d.get('p1',.3))),d.get('p_controls',d.get('risk_unexposed',d.get('p0',.15))))
    if m=='power_mean':return power_mean(d.get('n1',100),d.get('n2',100),d.get('sd',10),d.get('diff',5))
    if m=='random':return random_numbers(d['n'],d['low'],d['high'],d.get('seed'))
    raise ValueError(f'Calculator module not implemented: {m}')
