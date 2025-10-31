# lightweight utils retained for sample network and asset CSV
import networkx as nx, os, pandas as pd

def sample_network():
    G = nx.DiGraph()
    nodes = [
        ('Enterprise-1', 4, 'Domain Controller'),
        ('DMZ-1', 3, 'Jump Host'),
        ('IT-Switch', 3, 'Switch'),
        ('Engineering-HMI', 2, 'HMI'),
        ('PLC-1', 1, 'PLC'),
        ('PLC-2', 1, 'PLC'),
        ('Historian', 2, 'Historian'),
    ]
    for n,level,role in nodes:
        G.add_node(n, level=level, role=role)
    edges = [
        ('Enterprise-1','DMZ-1'),
        ('DMZ-1','Engineering-HMI'),
        ('Engineering-HMI','PLC-1'),
        ('Engineering-HMI','PLC-2'),
        ('IT-Switch','Enterprise-1'),
        ('PLC-1','Historian'),
        ('Enterprise-1','PLC-2'),
    ]
    for u,v in edges:
        G.add_edge(u,v)
    return G

def sample_asset_csv(path='data/sample_assets.csv'):
    rows = [
        {'name':'PLC-1','ip':'10.0.1.10','vendor':'VendorA','protocol':'Modbus','expected':'PLC'},
        {'name':'HMI-1','ip':'10.0.2.5','vendor':'VendorB','protocol':'OPC','expected':'HMI'},
        {'name':'Historian-1','ip':'10.0.3.20','vendor':'VendorC','protocol':'MQTT','expected':'Historian'},
        {'name':'TempSensor-1','ip':'10.0.4.8','vendor':'VendorD','protocol':'Proprietary','expected':'Sensor'},
    ]
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return path
