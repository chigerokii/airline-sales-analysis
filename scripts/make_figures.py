"""Графики для README. Запуск из корня репозитория: python scripts/make_figures.py"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
BLUE='#2b6cb0'; LIGHT='#90cdf4'; GREY='#a0aec0'; ORANGE='#dd6b20'
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False,
                     'axes.grid':True,'grid.alpha':.25,'axes.axisbelow':True,'legend.frameon':False})
f=lambda x,d=0: f'{x:,.{d}f}'.replace(',',' ').replace('.',',')
d=pd.read_csv('data/air_data.csv',sep=';'); d.columns=d.columns.str.lower().str.replace('﻿','')
d=d[d.revenue_amount>0].copy()
d['issue']=pd.to_datetime(d.issue_date); d['flight']=pd.to_datetime(d.flight_date_loc)
d['lead']=(d.flight-d.issue).dt.days
# 1. Помесячно
m=d.groupby(d.issue.dt.to_period('M')).agg(rev=('revenue_amount','sum'),n=('revenue_amount','size'),avg=('revenue_amount','mean'))
fig,ax=plt.subplots(figsize=(10,4))
x=np.arange(len(m)); bars=ax.bar(x,m.rev/1e6,color=[BLUE if p.month in (7,8) else LIGHT for p in m.index])
ax.set_xticks(x); ax.set_xticklabels([p.strftime('%m.%y') for p in m.index],fontsize=9); ax.set_ylabel('Выручка, млн')
ax2=ax.twinx(); ax2.plot(x,m.avg,'o-',color=ORANGE,label='средний чек'); ax2.set_ylabel('Средний чек',color=ORANGE); ax2.grid(False)
ax2.set_ylim(0,m.avg.max()*1.3); ax2.spines['right'].set_visible(True)
ax.set_title('Пик выручки в июле–августе, а средний чек с весны 2022 года вырос примерно на треть')
fig.tight_layout(); fig.savefig('images/monthly_revenue.png',dpi=130); plt.close()
# 2. Глубина бронирования
d['grp']=pd.cut(d.lead,[-1,6,29,89,10000],labels=['меньше недели','1–4 недели','1–3 месяца','больше 3 месяцев'])
g=d.groupby('grp',observed=True).agg(n=('revenue_amount','size'),avg=('revenue_amount','mean'),rev=('revenue_amount','sum'))
fig,axes=plt.subplots(1,2,figsize=(11,3.8))
b=axes[0].bar(g.index.astype(str),g.rev/g.rev.sum()*100,color=BLUE); axes[0].bar_label(b,[f(v,0)+'%' for v in g.rev/g.rev.sum()*100],padding=3)
axes[0].set_title('Доля выручки'); axes[0].set_yticks([]); axes[0].grid(False)
b=axes[1].bar(g.index.astype(str),g.avg,color=GREY); axes[1].bar_label(b,[f(v,0) for v in g.avg],padding=3)
axes[1].set_title('Средний чек'); axes[1].set_yticks([]); axes[1].grid(False); axes[1].set_ylim(0,g.avg.max()*1.25)
for a in axes: a.tick_params(axis='x',labelsize=9)
fig.suptitle('За сколько до вылета покупают билет: 80% выручки дают покупки за месяц и меньше,\nно средний чек у ранних и поздних покупок почти одинаковый',fontweight='bold',fontsize=11)
fig.tight_layout(); fig.savefig('images/booking_window.png',dpi=130,bbox_inches='tight'); plt.close()
# 3. Сегменты
segs={'Тип рейса':d.route_flight_type.map({'ВВЛ':'внутренние','МВЛ':'международные'}),
      'Программа лояльности':d.ffp_flag.fillna('нет').map({'FFP':'участники','нет':'не участники'}),
      'Канал продажи':d.sale_type.map({'ONLINE':'онлайн','OFFLINE':'офлайн'})}
fig,axes=plt.subplots(1,3,figsize=(12,3.6))
for ax,(name,s) in zip(axes,segs.items()):
    t=d.groupby(s).revenue_amount.agg(['sum','mean']); share=t['sum']/t['sum'].sum()*100
    b=ax.bar(t.index,share,color=[BLUE,LIGHT]); ax.bar_label(b,[f'{f(v,0)}%\nчек {f(c,0)}' for v,c in zip(share,t['mean'])],padding=3,fontsize=9)
    ax.set_title(name); ax.set_yticks([]); ax.set_ylim(0,115); ax.grid(False)
fig.suptitle('Доля выручки и средний чек по сегментам',fontweight='bold')
fig.tight_layout(); fig.savefig('images/segments.png',dpi=130,bbox_inches='tight'); plt.close()
print(m.round(1).to_string()); print(g); 
