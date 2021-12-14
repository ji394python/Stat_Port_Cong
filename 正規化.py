import pandas as pd

df = pd.read_csv('output_data\SHANGHAI.csv')
df['Standard_Time'] = df['Time At Port'].apply(lambda x: ''.join('_'.join('_'.join(x.split('d')).split('h')).split('m')).strip().replace(' ','').split('_'))
time = []
for i in df['Standard_Time'].values:
    i = [ 0 if value == '' else int(value) for value in i]
    try:
        if len(i) == 1:
            time.append(int(i[0])*60)
        elif len(i) == 2:
            time.append(int(i[0])*3600+int(i[1])*60)
        elif len(i) == 3:
            time.append(int(i[0])*86400+int(i[1])*3600+int(i[2])*60)
        else:
            print('三小拉',i)
    except:
        print(i)
        
df['Standard_Time'] = time
df = df[['Vessel Name', 'Port Call Type', 'Port Type', 'Port At Call',
       'Ata/atd11', 'Time At Port', 'Standard_Time', 'In Transit Port Calls',
       'Vessel Type - Detailed', 'Commercial Market']]

df.columns = ['Vessel Name', 'Port Call Type', 'Port Type', 'Port At Call',
       'Ata/atd11', 'Time At Port', 'Time At Port(sec)', 'In Transit Port Calls',
       'Vessel Type - Detailed', 'Commercial Market']

df.to_csv('SHANGHAI2.csv')

from datetime import datetime,timedelta

df['Time At Port(sec)']
df['Ata/atd11'].apply(lambda x: datetime.strptime(x.replace(' UTC',''),'%Y-%m-%d %H:%M'))
arrive = []
for i in  range(len(df)):
    x = datetime.strptime(df['Ata/atd11'].values[i].replace(' UTC',''),'%Y-%m-%d %H:%M') - timedelta(seconds=int(df['Time At Port(sec)'].values[i]))
    arrive.append(x)
    
df['Arrive Time'] = arrive