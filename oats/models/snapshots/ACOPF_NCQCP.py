import sys
sys.path.insert(1, 'C:\\Users\\richn\\OneDrive - University of Strathclyde\\General - EEE_STU_NayerPhD\\#CODEZONE\\oats_v2')

import idaes
import pyomo.environ as pyo
from pyomo.contrib import appsi
import pandas as pd
from oats.utils.df_utils import *
from data_io import load_case
from typing import List, Dict, Tuple, Union, Any
import sys
from io import StringIO
buf = StringIO()

m = pyo.AbstractModel()
i = m.create_instance()


def import_case():
# ──────────────────────────────────────────────────────────────────────────────────────────
# Import Case Data From Excel File
# ──────────────────────────────────────────────────────────────────────────────────────────
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Define Excel Testcase
    # ──────────────────────────────────────────────────────────────────────────────────────────
    testcase = "2bus_testcase.xlsx"

    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Define Static Data Import Configuration
    # ──────────────────────────────────────────────────────────────────────────────────────────
    static_data_config: Dict[str, Dict[str, Any]] = {
        # ── Bus Excel Sheet ──────────────────────────────────────────────────────────
        'bus': {
            'key': 'busses',
            'col_types': {'name': pd.StringDtype(), #bus name
                            'baseKV': float, #basekVA for bus
                            'type': int, #Type of bus 
                            'zone': pd.StringDtype(), #Bus Zone
                            'VLB': float, #Voltage Lower Bound [pu]
                            'VUB': float #Voltage Upper Bound [pu]
            },
            'dropna': True,
            'filter_active': True
        },
        # ── Demands Excel Sheet ──────────────────────────────────────────────────────────
        'demand': {
            'key': 'demands',
            'col_types': {'name': pd.StringDtype(), #Demand Name
                            'busname': pd.StringDtype(), #Demand Bus
                            'real': float, #Real Power Demand [MW]
                            'reactive': float, #Reactive Power Demand [MVAR]
                            'stat': int, #Demand Status (0 = Inactive, 1 = Active)
                            'VOLL': int #Value of Lost Load [£/MW]
            },
            'dropna': True,
            'filter_active': True
        },
        # ── Branch Excel Sheet ──────────────────────────────────────────────────────────
        'branch': {
            'key': 'branches',
            'col_types': {'name': pd.StringDtype(), #Branch Name
                            'from_busname': pd.StringDtype(), #From Bus
                            'to_busname': pd.StringDtype(), #To Bus
                            'stat': int, #Branch Status (0 = Inactive, 1 = Active)
                            'r': float, #Line Resistance [pu]
                            'x': float, #Line Reactance [pu]
                            'b': float, #Line Shunt Susceptance [pu]
                            'ShortTermRating': int, #Line Short Term Rating [MVA]
                            'ContinuousRating': int #Line Continuous Rating [MVA]
            },
            'dropna': True,
            'filter_active': True
        },
        # ── Transformer Excel Sheet ──────────────────────────────────────────────────────────
        'transformer': {
            'key': 'transformers',
            'col_types': {'name': pd.StringDtype(), #Transformer Name
                            'from_busname': pd.StringDtype(), #Transformer From Bus
                            'to_busname': pd.StringDtype(), #Transformer To Bus
                            'type': pd.StringDtype(), #Transformer Type
                            'stat': int, #Transformer Status (0 = Inactive, 1 = Active)
                            'r': float, #Transformer Resistance [pu]
                            'x': float, #Transformer Reactance [pu]
                            'b': float, #Transformer Shunt Susceptance [pu]
                            'ShortTermRating': int, #Transformer Short Term Rating [MVA]
                            'ContinuousRating': int #Transformer Continuous Rating [MVA]
            },
            'dropna': True,
            'filter_active': True
        },
        # ── Generator Excel Sheet ──────────────────────────────────────────────────────────
        'generator': {
            'key': 'generators',
            'col_types': {'busname': pd.StringDtype(), #Generator Bus
                            'name': pd.StringDtype(), #Generator Name
                            'export_policy': pd.StringDtype(), #Generator Export Policy
                            'lifo_group': pd.StringDtype(), #Generator LIFO Group
                            'lifo_position': pd.StringDtype(), #Generator LIFO Position
                            'prorata_groups': pd.StringDtype(), #Generator Prorata Groups
                            'stat': int, #Generator Status (0 = Inactive, 1 = Active)
                            'type': pd.StringDtype(), #Generator Type???
                            'PGMINGEN': float, #Minimum Real Power Generation [MW]
                            'PGLB': float, #Generator Real Power Lower Bound [MW]
                            'PGUB': float, #Generator Real Power Upper Bound [MW]
                            'QGLB': float, #Generator Reactive Power Lower Bound [MVAR]
                            'QGUB': float, #Generator Reactive Power Upper Bound [MVAR]
                            'FuelType': pd.StringDtype(), #Generator Fuel Type
                            'synchronous': pd.StringDtype(), #Generator Synchronous Status (Yes/No)
                            'costc1': float, #Generator Variable Cost [£/MW]
                            'costc0': float, #Generator Fixed Cost [£]
                            'bid': float, #Generator Bid Cost [£/MW]
                            'offer': float #Generator Offer Cost [£/MW]
            },
            'dropna': True,
            'filter_active': True
        },
        # ── baseMVA Excel Sheet ──────────────────────────────────────────────────────────
        'baseMVA': {
            'key': 'baseMVA',
            'col_types': {'baseMVA': float},
            'dropna': True,
            'filter_active': False
        }
            }

    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Define Series Data Configuration
    # ──────────────────────────────────────────────────────────────────────────────────────────
    series_data_config: Dict[str, Dict[str, Any]] = {
        # ── Real Power Demand [MW] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_PD': {
            'key': 'ts_PD',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Value of Lost Load [£/MWh] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_VOLL': {
            'key': 'ts_VOLL',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Power Line Minimum Apparent Power Flow [MVA] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_Lmax': {
            'key': 'ts_Lmax',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Power Line Maximum Apparent Power Flow [MVA] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_TLmax': {
            'key': 'ts_TLmax',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Generator Minimum Real Power Out [MW] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_PGLB': {
            'key': 'ts_PGLB',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Generator Maximum Real Power Out [MW] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_PGUB': {
            'key': 'ts_PGUB',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Generator Bid Price [£/MW] (Rows = Timesteps, Columns = Demand Name) ──────────────────────────────────────────────────────────
        'ts_bid': {
            'key': 'ts_bid',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        }
    }

    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Load Excel Case into 'case' object
    # ──────────────────────────────────────────────────────────────────────────────────────────
    case = load_case.Case()
    case._load_excel_case(testcase, static_data_config, series = True, series_config = series_data_config)
    return case
# ──────────────────────────────────────────────────────────────────────────────────────────


def initialise_sets(case):
# ──────────────────────────────────────────────────────────────────────────────────────────
# Initialise Sets
# ──────────────────────────────────────────────────────────────────────────────────────────

    def bus_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Bus Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Bus Names [Bus1_name, Bus2_name,...] ──────────────────────────────────────────────────────────
        BUS_NAMES = filter_df(case.busses, [['type', '!=', 0]])['name'].to_list()
        i.BUSSES = pyo.Set(initialize = BUS_NAMES)

        # ── Slack Bus [Slackbus_name] ──────────────────────────────────────────────────────────
        SLACK_BUS = filter_df(case.busses, [['type', '==', 3]])['name'].to_list()
        i.SLACK_BUS = pyo.Set(initialize = SLACK_BUS)
    
    def generation_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Generator Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generator Names [Generator1_name, Generator2_name,...] ──────────────────────────────────────────────────────────
        GENERATOR_NAMES = case.generators['name'].to_list()
        i.GENERATORS = pyo.Set(initialize = GENERATOR_NAMES)

        # ── Generators Indexed to Sets (Dict: {Bus: [Gen1, Gen2, ...]}) ──────────────────────────────────────────────────────────
        GENERATORS_AT_BUSSES = df_merge_to_dict(case.busses, "name", case.generators, "name","busname")
        i.GENERATORS_AT_BUSSES = pyo.Set(i.BUSSES, initialize = GENERATORS_AT_BUSSES)

    def branch_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Branch Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Branch Names [Branch1_name, Branch2_name,...] ──────────────────────────────────────────────────────────
        BRANCH_NAMES = case.branches['name'].to_list()
        i.BRANCHES = pyo.Set(initialize = BRANCH_NAMES)

        # ── Branches To_Bus Indexed to Sets (Dict: {Bus: [To_Bus1, To_Bus2,...]}) ──────────────────────────────────────────────────────────
        BUS_BRANCHES_IN = df_merge_to_dict(case.busses, "name", case.branches, "name", "to_busname")
        i.BUS_BRANCHES_IN = pyo.Set(i.BUSSES, initialize = BUS_BRANCHES_IN)

        # ── Branches From_Bus Indexed to Sets (Dict: {Bus: [From_Bus1, From_Bus2,...]}) ──────────────────────────────────────────────────────────
        BUS_BRANCHES_OUT = df_merge_to_dict(case.busses, "name", case.branches, "name", "from_busname")
        i.BUS_BRANCHES_OUT = pyo.Set(i.BUSSES, initialize = BUS_BRANCHES_OUT)

        # ── Busses Indexed to Branches (Dict: {Branch: [(To_Bus1, From_Bus1), (To_Bus1, From_Bus2),...]}) ──────────────────────────────────────────────────────────
        BRANCH_BUSSES = df_to_zipped_param_list(case.branches, "name", ["from_busname", "to_busname"])
        i.BRANCH_BUSSES = pyo.Set(i.BRANCHES, initialize = BRANCH_BUSSES, ordered = True)

    def transformer_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Transformer Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Set of Transformer Names [Transformer1_name, Transformer2_name,...] ──────────────────────────────────────────────────────────
        TRANSFORMER_NAMES = case.transformers['name'].to_list()
        i.TRANSFORMERS = pyo.Set(initialize = TRANSFORMER_NAMES)

        # ── Set of Transformer To_Bus Indexed to Sets (Dict: {Bus: [To_Bus1, To_Bus2,...]}) ──────────────────────────────────────────────────────────
        BUS_TRANSFORMERS_IN = df_merge_to_dict(case.busses, "name", case.transformers, "name", "to_busname")
        i.BUS_TRANSFORMERS_IN = pyo.Set(i.BUSSES, initialize = BUS_TRANSFORMERS_IN)

        # ── Set of Transformer From_Bus Indexed to Sets (Dict: {Bus: [From_Bus1, From_Bus2,...]}) ──────────────────────────────────────────────────────────
        BUS_TRANSFORMERS_OUT = df_merge_to_dict(case.busses, "name", case.transformers, "name", "from_busname")
        i.BUS_TRANSFORMERS_OUT = pyo.Set(i.BUSSES, initialize = BUS_TRANSFORMERS_OUT)

        # ── Set of Busses Indexed to Transformers (Dict: {Transformer: [(To_Bus1, From_Bus1), (To_Bus1, From_Bus2),...]}) ──────────────────────────────────────────────────────────
        TRANSFORMER_BUSSES = df_to_zipped_param_list(case.transformers, "name", ["from_busname", "to_busname"])
        i.TRANSFORMER_BUSSES = pyo.Set(i.TRANSFORMERS, initialize = TRANSFORMER_BUSSES, ordered = True)


    def demand_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Demand Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Set of Demands [Demand1_name, Demand2_name,...] ──────────────────────────────────────────────────────────
        DEMAND_NAMES = case.demands['name'].to_list()
        i.DEMANDS = pyo.Set(initialize = DEMAND_NAMES)

        # ── Set of Negative Demands [NegativeDemand1_name, NegativeDemand2_name,...] ──────────────────────────────────────────────────────────
        DEMANDS_NEGATIVE_REAL = filter_df(case.demands, [['real', '<', 0]])
        i.DEMANDS_NEGATIVE_REAL = pyo.Set(initialize = DEMANDS_NEGATIVE_REAL)

        # ── Set of Demands Indexed to Busses (Dict: {Bus: [Demand1, Demand2,...]}) ──────────────────────────────────────────────────────────
        BUS_DEMANDS =  df_merge_to_dict(case.busses, 'name', case.demands, 'name', 'busname')
        i.BUS_DEMANDS = pyo.Set(i.BUSSES, initialize = BUS_DEMANDS)

    # Assign Sets to Model ─────────────────────────────────────────────────────────────────────────
    bus_sets()
    generation_sets()
    branch_sets()
    transformer_sets()
    demand_sets()
# ──────────────────────────────────────────────────────────────────────────────────────────


def initialise_parameters(case):
# ──────────────────────────────────────────────────────────────────────────────────────────
# Initialise Parameters
# ──────────────────────────────────────────────────────────────────────────────────────────
    def branch_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Branch Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Branch Apparent Power Max (Continuous) [p.u.]  Assumes MW input ──────────────────────────────────────────────────────────
        Branch_Apparent_Power_Max_Continuous = df_to_scaled_param_dict(case.branches, 'name', 'ContinuousRating', (1/case.baseMVA))
        i.Branch_Apparent_Power_Max_Continuous = pyo.Param(i.BRANCHES, domain = pyo.NonNegativeReals, initialize = Branch_Apparent_Power_Max_Continuous)

        # ── Branch Resistance R [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Branch_Resistance = df_to_param_dict(case.branches, 'name', 'r')
        i.Branch_Resistance = pyo.Param(i.BRANCHES, domain = pyo.Reals, initialize=Branch_Resistance)

        # ── Branch Reactance X [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Branch_Reactance = df_to_param_dict(case.branches, 'name', 'x')
        i.Branch_Reactance = pyo.Param(i.BRANCHES, domain = pyo.Reals, initialize = Branch_Reactance)

        # ── Branch Shunt Susceptance B [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Branch_Shunt_Susceptance = df_to_param_dict(case.branches, 'name', 'b')
        i.Branch_Shunt_Susceptance = pyo.Param(i.BRANCHES, domain = pyo.Reals, initialize = Branch_Shunt_Susceptance)

        # ── Branch Conductance G [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        i.Branch_Conductance= pyo.Param(i.BRANCHES, domain = pyo.Reals, initialize = lambda i,b: i.Branch_Resistance[b]/(i.Branch_Resistance[b]**2 + i.Branch_Reactance[b]**2))

        # ── Branch Susceptance B [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        i.Branch_Susceptance = pyo.Param(i.BRANCHES, domain = pyo.Reals, initialize = lambda i,b: -i.Branch_Reactance[b]/(i.Branch_Resistance[b]**2 + i.Branch_Reactance[b]**2))


    def transformer_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Transformer Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Transformer Apparent Power Max (Continuous) [p.u.]  Assumes ME input ──────────────────────────────────────────────────────────
        Transformer_Apparent_Power_Max_Continuous = df_to_scaled_param_dict(case.transformers, 'name', 'ContinuousRating', (1/case.baseMVA))
        i.Transformer_Apparent_Power_Max_Continuous = pyo.Param(i.TRANSFORMERS, domain = pyo.NonNegativeReals, initialize = Transformer_Apparent_Power_Max_Continuous)

        # ── Transformer Resistance R [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Transformer_Resistance = df_to_param_dict(case.transformers, 'name', 'r')
        i.Transformer_Resistance = pyo.Param(i.TRANSFORMERS, domain = pyo.Reals, initialize=Transformer_Resistance)

        # ── Transformer Reactance X [p.u.]  Assumes p.u. input ──────────────────────────────────────────────────────────
        Transformer_Reactance = df_to_param_dict(case.transformers, 'name', 'x')
        i.Transformer_Reactance = pyo.Param(i.TRANSFORMERS, domain = pyo.Reals, initialize = Transformer_Reactance)

        # ── Transformer Shunt Susceptance B [p.u.]  Assumes p.u. input ──────────────────────────────────────────────────────────
        Transformer_Shunt_Susceptance = df_to_param_dict(case.transformers, 'name', 'b')
        i.Transformer_Shunt_Susceptance = pyo.Param(i.TRANSFORMERS, domain = pyo.Reals, initialize = Transformer_Shunt_Susceptance)

        # ── Transformer Conductance G [p.u.]  Assumes p.u. input ──────────────────────────────────────────────────────────
        i.Transformer_Conductance= pyo.Param(i.TRANSFORMERS, domain = pyo.Reals, initialize = lambda i,t: i.Transformer_Resistance[t]/(i.Transformer_Resistance[t]**2 + i.Transformer_Reactance[t]**2))
        
        # ── Transformer Susceptance B [p.u.]  Assumes p.u. input ──────────────────────────────────────────────────────────
        i.Transformer_Susceptance = pyo.Param(i.TRANSFORMERS, domain = pyo.Reals, initialize = lambda i,t: -i.Transformer_Reactance[t]/(i.Transformer_Resistance[t]**2 + i.Transformer_Reactance[t]**2))
        

    def demand_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Demand Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Real Power Demand (Continuous) [p.u.] Assumes MW Input ──────────────────────────────────────────────────────────
        Real_Power_Demand = df_to_scaled_param_dict(case.demands, 'name', 'real', (1/case.baseMVA))
        i.Real_Power_Demand = pyo.Param(i.DEMANDS, domain = pyo.Reals, initialize = Real_Power_Demand)
        
        # ── Reactive Power Demand (Continuous) [p.u.] Assumes MVAR Input ──────────────────────────────────────────────────────────
        Reactive_Power_Demand = df_to_scaled_param_dict(case.demands, 'name', 'reactive', (1/case.baseMVA))
        i.Reactive_Power_Demand = pyo.Param(i.DEMANDS, domain = pyo.Reals, initialize = Reactive_Power_Demand)
        
        # ── Value of Lost Load [£/MW] ──────────────────────────────────────────────────────────
        Voll = Voll = df_to_scaled_param_dict(case.demands, 'name', 'VOLL', (1/case.baseMVA))
        i.Voll = pyo.Param(i.DEMANDS, domain = pyo.Reals, initialize = Voll)
    
    def generator_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Generator Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generator Real Power Output Max [p.u.] Assumes MW Input ──────────────────────────────────────────────────────────
        Gen_Real_Power_Max = df_to_scaled_param_dict(case.generators, 'name', 'PGUB', (1/case.baseMVA))
        i.Gen_Real_Power_Max = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Real_Power_Max)
        
        # ── Generator Real Power Output Min [p.u.] Assumes MW Input ──────────────────────────────────────────────────────────
        Gen_Real_Power_Min = df_to_scaled_param_dict(case.generators, 'name', 'PGLB', (1/case.baseMVA))
        i.Gen_Real_Power_Min = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Real_Power_Min)
        
        # ── Generator Reactive Power Output Max [p.u.] Assumes MVAR Input ──────────────────────────────────────────────────────────
        Gen_Reactive_Power_Max = df_to_scaled_param_dict(case.generators, 'name', 'QGUB', (1/case.baseMVA))
        i.Gen_Reactive_Power_Max = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Reactive_Power_Max)
        
        # ── Generator Reactive Power Output Min [p.u.] Assumes MVAR Input ──────────────────────────────────────────────────────────
        Gen_Reactive_Power_Min = df_to_scaled_param_dict(case.generators, 'name', 'QGLB', (1/case.baseMVA))
        i.Gen_Reactive_Power_Min = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Reactive_Power_Min)
        
        # ── Generator Fixed Price [£] ──────────────────────────────────────────────────────────
        Gen_Price_c0 = df_to_param_dict(case.generators, 'name', 'costc0')
        i.Gen_Price_c0 = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Price_c0)
        
        # ── Generator Variable Price [£/MWh] ──────────────────────────────────────────────────────────
        Gen_Price_c1 = df_to_param_dict(case.generators, 'name', 'costc1')
        i.Gen_Price_c1 = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Price_c1)
        
        # ── Generator Bid Price [£/MWh] ──────────────────────────────────────────────────────────
        Gen_Price_Bid = df_to_param_dict(case.generators, 'name', 'bid')
        i.Gen_Price_Bid = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Price_Bid)
        
        # ── Generator Offer Price [£/MWh] ──────────────────────────────────────────────────────────
        Gen_Price_Offer = df_to_param_dict(case.generators, 'name', 'offer')
        i.Gen_Price_Offer = pyo.Param(i.GENERATORS, domain = pyo.Reals, initialize = Gen_Price_Offer)

    def bus_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Bus Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Bus Voltage Lower Bound [p.u.] ────────────────────────────────────────────────────────
        Bus_VLB = df_to_param_dict(case.busses, 'name', 'VLB')
        i.Bus_VLB = pyo.Param(i.BUSSES, domain = pyo.Reals, initialize = Bus_VLB)

        # ── Bus Voltage Upper Bound [p.u.] ────────────────────────────────────────────────────────
        Bus_VUB = df_to_param_dict(case.busses, 'name', 'VUB')  
        i.Bus_VUB = pyo.Param(i.BUSSES, domain = pyo.Reals, initialize = Bus_VUB)

    def per_unit_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Per Unit System Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── System Base MVA [MVA] ──────────────────────────────────────────────────────────
        i.BaseMVA = pyo.Param(domain = pyo.Reals, initialize = case.baseMVA)

    # ── Call Functions to Create Parameters ──────────────────────────────────────────────────────────
    branch_parameters()
    transformer_parameters()
    demand_parameters()
    generator_parameters()
    bus_parameters()
    per_unit_parameters()
# ───────────────────────────────────────────────────────────────────────────────────────────────


def initialise_variables():
# ──────────────────────────────────────────────────────────────────────────────────────────
# Initialise Variables
# ──────────────────────────────────────────────────────────────────────────────────────────
    def generator_variables():
        i.generator_real_power_out = pyo.Var(i.GENERATORS, domain = pyo.Reals)
        i.generator_real_power_bid = pyo.Var(i.GENERATORS, domain = pyo.NonNegativeReals)
        i.generator_real_power_offer = pyo.Var(i.GENERATORS, domain = pyo.NonNegativeReals)
        i.generator_reactive_power_out = pyo.Var(i.GENERATORS, domain = pyo.Reals)
        i.generator_reactive_power_bid = pyo.Var(i.GENERATORS, domain = pyo.NonNegativeReals)
        i.generator_reactive_power_offer = pyo.Var(i.GENERATORS, domain = pyo.NonNegativeReals)

    def demand_variables():
        i.demand_real_power_met = pyo.Var(i.DEMANDS, domain=pyo.Reals)
        i.demand_reactive_power_met = pyo.Var(i.DEMANDS, domain=pyo.Reals)
        i.demand_proportion_met = pyo.Var(i.DEMANDS, domain = pyo.NonNegativeReals, bounds = (0,1), initialize = 1)

    def branch_variables():
        i.branch_real_power_flow_atob = pyo.Var(i.BRANCHES, domain = pyo.Reals)
        i.branch_reactive_power_flow_atob = pyo.Var(i.BRANCHES, domain = pyo.Reals)
        i.branch_real_power_flow_btoa = pyo.Var(i.BRANCHES, domain = pyo.Reals)
        i.branch_reactive_power_flow_btoa = pyo.Var(i.BRANCHES, domain = pyo.Reals)

    def transformer_variables():
        i.transformer_voltage_angle_difference = pyo.Var(i.TRANSFORMERS, domain = pyo.Reals)
        i.transformer_real_power_flow_atob = pyo.Var(i.TRANSFORMERS, domain = pyo.Reals)
        i.transformer_reactive_power_flow_atob = pyo.Var(i.TRANSFORMERS, domain = pyo.Reals)
        i.transformer_real_power_flow_btoa = pyo.Var(i.TRANSFORMERS, domain = pyo.Reals)
        i.transformer_reactive_power_flow_btoa = pyo.Var(i.TRANSFORMERS, domain = pyo.Reals)

    def bus_variables():
        i.bus_voltage_angle = pyo.Var(i.BUSSES, domain = pyo.Reals)
        i.bus_voltage_magnitude = pyo.Var(i.BUSSES, domain = pyo.NonNegativeReals, initialize = 1.0)


    # ── Call Functions to Assign Variables to Model  ──────────────────────────────────────
    generator_variables()
    demand_variables()
    branch_variables()
    transformer_variables()
    bus_variables()
# ──────────────────────────────────────────────────────────────────────────────────────────


def initialise_constraints():
# ──────────────────────────────────────────────────────────────────────────────────────────
# Initialise Constraints
# ──────────────────────────────────────────────────────────────────────────────────────────
    def network_constraints():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Network Constraints
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── KCL Real Power Constraint ──────────────────────────────────────────────────────────
        @i.Constraint(i.BUSSES)
        def KCL_ACOPF_real_power_constraint(i, bus):
            return sum(i.generator_real_power_out[generator] for generator in i.GENERATORS_AT_BUSSES[bus]) ==\
                   + sum(i.branch_real_power_flow_atob[line] for line in i.BUS_BRANCHES_OUT[bus])\
                   + sum(i.branch_real_power_flow_btoa[line] for line in i.BUS_BRANCHES_IN[bus])\
                   + sum(i.transformer_real_power_flow_atob[transformer] for transformer in i.BUS_TRANSFORMERS_OUT[bus])\
                   + sum(i.transformer_real_power_flow_btoa[transformer] for transformer in i.BUS_TRANSFORMERS_IN[bus])\
                   + sum(i.demand_real_power_met[demand] for demand in i.BUS_DEMANDS[bus])

        # ── KCL Reactive Power Constraint ──────────────────────────────────────────────────────────
        @i.Constraint(i.BUSSES)
        def KCL_ACOPF_reactive_power_constraint(i, bus):
            return + sum(i.generator_reactive_power_out[generator] for generator in i.GENERATORS_AT_BUSSES[bus]) ==\
                   + sum(i.branch_reactive_power_flow_atob[line] for line in i.BUS_BRANCHES_OUT[bus])\
                   + sum(i.branch_reactive_power_flow_btoa[line] for line in i.BUS_BRANCHES_IN[bus])\
                   + sum(i.transformer_reactive_power_flow_atob[transformer] for transformer in i.BUS_TRANSFORMERS_OUT[bus])\
                   + sum(i.transformer_reactive_power_flow_btoa[transformer] for transformer in i.BUS_TRANSFORMERS_IN[bus])\
                   + sum(i.demand_reactive_power_met[demand] for demand in i.BUS_DEMANDS[bus])

        # ── KVL Constraints for Branches ──────────────────────────────────────────────────────────
        # ── Branch Real Power Out
        @i.Constraint(i.BRANCHES)
        def branch_real_KVL_ACOPF_atob(i,branch):
            a = i.BRANCH_BUSSES[branch].at(1)
            b = i.BRANCH_BUSSES[branch].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = a_angle - b_angle

            return i.branch_real_power_flow_atob[branch] == \
                      (V_a_rms**2)*i.Branch_Conductance[branch]\
                    - (V_a_rms*V_b_rms)*\
                        (i.Branch_Conductance[branch]*pyo.cos(theta)+i.Branch_Susceptance[branch]*pyo.sin(theta))

        # ── Branch Real Power Back
        @i.Constraint(i.BRANCHES)
        def branch_real_KVL_ACOPF_btoa(i,branch):
            a = i.BRANCH_BUSSES[branch].at(1)
            b = i.BRANCH_BUSSES[branch].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = b_angle- a_angle

            return i.branch_real_power_flow_btoa[branch] == \
                      (V_b_rms**2)*i.Branch_Conductance[branch]\
                    - (V_a_rms*V_b_rms)*\
                        (i.Branch_Conductance[branch]*pyo.cos(theta)+i.Branch_Susceptance[branch]*pyo.sin(theta))

        # ── Branch Reactive Power Out
        @i.Constraint(i.BRANCHES)
        def branch_reactive_KVL_ACOPF_atob(i,branch):
            a = i.BRANCH_BUSSES[branch].at(1)
            b = i.BRANCH_BUSSES[branch].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = a_angle - b_angle

            return i.branch_reactive_power_flow_atob[branch] == \
                      -(V_a_rms**2)*(i.Branch_Shunt_Susceptance[branch]/2 + i.Branch_Susceptance[branch])\
                      - (V_a_rms*V_b_rms)*\
                            (i.Branch_Conductance[branch]*pyo.sin(theta)-i.Branch_Susceptance[branch]*pyo.cos(theta))

        # ── Branch Reactive Power Back
        @i.Constraint(i.BRANCHES)
        def branch_reactive_KVL_ACOPF_btoa(i,branch):
            a = i.BRANCH_BUSSES[branch].at(1)
            b = i.BRANCH_BUSSES[branch].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = b_angle - a_angle

            return i.branch_reactive_power_flow_btoa[branch] == \
                      -(V_b_rms**2)*(i.Branch_Shunt_Susceptance[branch]/2 + i.Branch_Susceptance[branch])\
                      - (V_a_rms*V_b_rms)*\
                            (i.Branch_Conductance[branch]*pyo.sin(theta)-i.Branch_Susceptance[branch]*pyo.cos(theta))

        # ── KVL Constraints for Transformers  ──────────────────────────────────────────────────────────
        # ── KVL Transformer Real Power Out
        @i.Constraint(i.TRANSFORMERS)
        def transformer_real_KVL_ACOPF_atob(i,transformer):
            a = i.TRANSFORMER_BUSSES[transformer].at(1)
            b = i.TRANSFORMER_BUSSES[transformer].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = a_angle - b_angle

            return i.transformer_real_power_flow_atob[transformer] == \
                      (V_a_rms**2)*i.Transformer_Conductance[transformer]\
                    - (V_a_rms*V_b_rms)*\
                        (i.Transformer_Conductance[transformer]*pyo.cos(theta)+i.Transformer_Susceptance[transformer]*pyo.sin(theta))

        # ── KVL Transformer Real Power Back
        @i.Constraint(i.TRANSFORMERS)
        def transformer_real_KVL_ACOPF_btoa(i,transformer):
            a = i.TRANSFORMER_BUSSES[transformer].at(1)
            b = i.TRANSFORMER_BUSSES[transformer].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = b_angle - a_angle

            return i.transformer_real_power_flow_btoa[transformer] == \
                      (V_b_rms**2)*i.Transformer_Conductance[transformer]\
                    - (V_a_rms*V_b_rms)*\
                        (i.Transformer_Conductance[transformer]*pyo.cos(theta)+i.Transformer_Susceptance[transformer]*pyo.sin(theta))

        # ── KVL Transformer Reactive Power Out
        @i.Constraint(i.TRANSFORMERS)
        def transformer_reactive_KVL_ACOPF_atob(i,transformer):
            a = i.TRANSFORMER_BUSSES[transformer].at(1)
            b = i.TRANSFORMER_BUSSES[transformer].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = a_angle - b_angle

            return i.transformer_reactive_power_flow_atob[transformer] == \
                      -(V_a_rms**2)*(i.Transformer_Shunt_Susceptance[transformer]/2 + i.Transformer_Susceptance[transformer])\
                      - (V_a_rms*V_b_rms)*\
                            (i.Transformer_Conductance[transformer]*pyo.sin(theta)-i.Transformer_Susceptance[transformer]*pyo.cos(theta))
                      
        # ── KVL Tranformer Reactive Power Back
        @i.Constraint(i.TRANSFORMERS)
        def transformer_reactive_KVL_ACOPF_btoa(i,transformer):
            a = i.TRANSFORMER_BUSSES[transformer].at(1)
            b = i.TRANSFORMER_BUSSES[transformer].at(2)
            V_a_rms = i.bus_voltage_magnitude[a]
            V_b_rms = i.bus_voltage_magnitude[b]
            a_angle = i.bus_voltage_angle[a]
            b_angle = i.bus_voltage_angle[b]
            theta = b_angle - a_angle

            return i.transformer_reactive_power_flow_btoa[transformer] == \
                      -(V_b_rms**2)*(i.Transformer_Shunt_Susceptance[transformer]/2 + i.Transformer_Susceptance[transformer])\
                      - (V_a_rms*V_b_rms)*\
                            (i.Transformer_Conductance[transformer]*pyo.sin(theta)-i.Transformer_Susceptance[transformer]*pyo.cos(theta))

        # ── Voltage Reference Bus  ──────────────────────────────────────────────────────────
        @i.Constraint(i.BUSSES)
        def voltage_ref_bus_angle(i,bus):
            ref_bus = filter_df(case.busses, [['type', '==', 3]])['name'].to_list()
            if bus in ref_bus:
                return i.bus_voltage_angle[bus] == 0
            else:
                return pyo.Constraint.Skip

        @i.Constraint(i.BUSSES)
        def voltage_ref_bus_magnitude(i,bus):
            ref_bus = filter_df(case.busses, [['type', '==', 3]])['name'].to_list()
            if bus in ref_bus:
                return i.bus_voltage_magnitude[bus] == 1
            else:
                return pyo.Constraint.Skip

        # ── Bus Voltage Limits  ──────────────────────────────────────────────────────────
        # ── Bus Minimum Voltage
        @i.Constraint(i.BUSSES)
        def voltage_min(i, bus):
            return i.bus_voltage_magnitude[bus] >= i.Bus_VLB[bus]
        
        # ── Bus Maximum Voltage
        @i.Constraint(i.BUSSES)
        def voltage_max(i, bus):
            return i.bus_voltage_magnitude[bus] <= i.Bus_VUB[bus]

        # ── Power Line Power Flow Bounds  ──────────────────────────────────────────────────────────
        # ── Power Line Flow Out Limit
        @i.Constraint(i.BRANCHES)
        def branch_apparent_power_flow_UB(i, branch):
            return i.branch_real_power_flow_atob[branch]**2 + i.branch_reactive_power_flow_atob[branch]**2 <= i.Branch_Apparent_Power_Max_Continuous[branch]**2

        # ── Power Line Flow Back Limit
        @i.Constraint(i.BRANCHES)
        def branch_apparent_power_flow_UB_reverse(i, branch):
            return i.branch_real_power_flow_btoa[branch]**2 + i.branch_reactive_power_flow_btoa[branch]**2 <= i.Branch_Apparent_Power_Max_Continuous[branch]**2

        # ── Transformer Power Flow Bounds  ──────────────────────────────────────────────────────────
        # ── Tranformer Flow Out Limit
        @i.Constraint(i.TRANSFORMERS)
        def transformer_real_power_flow_UB(i, transformer):
            return i.transformer_real_power_flow_atob[transformer]**2 + i.transformer_reactive_power_flow_atob[transformer]**2 <= i.Transformer_Apparent_Power_Max_Continuous[transformer]**2

        # ── Transformer Flow Back Limit
        @i.Constraint(i.TRANSFORMERS)
        def transformer_real_power_flow_UB_reverse(i, transformer):
            return i.transformer_real_power_flow_btoa[transformer]**2 + i.transformer_reactive_power_flow_btoa[transformer]**2 <= i.Transformer_Apparent_Power_Max_Continuous[transformer]**2
        
    def demand_constraints():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Demand Constraints
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Demand Real Power Constraint
        @i.Constraint(i.DEMANDS)
        def demand_real_power_constraint(i, demand):
            return  i.demand_real_power_met[demand] == i.demand_proportion_met[demand] * i.Real_Power_Demand[demand]

        # ── Demand Reactive Power Constraint
        @i.Constraint(i.DEMANDS)
        def demand_reactive_power_constraint(i, demand):
            return  i.demand_reactive_power_met[demand] == i.demand_proportion_met[demand] * i.Reactive_Power_Demand[demand]

        # ── Always Meet Negative Real Power Demand Constraint
        negative_demands = filter_df(case.demands, [['real', '<', 0]])['name'].to_list()
        @i.Constraint(i.DEMANDS)
        def demand_always_meet_ngtve_demand(i, demand):
            if demand in negative_demands:
                return i.demand_proportion_met[demand] == 1
            else:
                return pyo.Constraint.Skip
    
    def generation_constraints():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Generation Constraints
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generation Real Power Lower Bound
        @i.Constraint(i.GENERATORS)
        def generation_real_power_LB(i, gen):
            return i.generator_real_power_out[gen] >= i.Gen_Real_Power_Min[gen]

        # ── Generation Real Power Upper Bound
        @i.Constraint(i.GENERATORS)
        def generation_real_power_UB(i, gen):
            return i.generator_real_power_out[gen] <= i.Gen_Real_Power_Max[gen]

        # ── Generation Reactive Power Lower Bound
        @i.Constraint(i.GENERATORS)
        def generation_reactive_power_LB(i, gen):
            return i.generator_reactive_power_out[gen] >= i.Gen_Reactive_Power_Min[gen]

        # ── Generation Reactive Power Upper Bound
        @i.Constraint(i.GENERATORS)
        def generation_reactive_power_UB(i, gen):
            return i.generator_reactive_power_out[gen] <= i.Gen_Reactive_Power_Max[gen]

    # ── Call Functions to Add Constraints to Model  ──────────────────────────────────────────────────────────
    network_constraints()
    demand_constraints()
    generation_constraints()
# ──────────────────────────────────────────────────────────────────────────────────────────
   

# ──────────────────────────────────────────────────────────────────────────────────────────
# Objective Function
# ──────────────────────────────────────────────────────────────────────────────────────────
def objective_marginal_cost(i):
    rnd = np.random.default_rng(100)

    obj = sum((i.Gen_Price_c1[gen]+rnd.random())*i.generator_real_power_out[gen] for gen in i.GENERATORS) +\
        sum(i.Voll[demand]*(1-i.demand_proportion_met[demand])*i.Real_Power_Demand[demand] for demand in i.DEMANDS)
    return obj


#Import Case, Initialise Sets/Params/Vars/Constraints
case = import_case()
initialise_sets(case)
initialise_parameters(case)
initialise_variables()
initialise_constraints()

#Define Model Objective
i.obj = pyo.Objective(rule = objective_marginal_cost(i), sense = pyo.minimize)

#Solve Model
def gurobi_solver():
    with pyo.SolverFactory(
        "gurobi_persistent",
        # solver_io = "appsi_gurobi",
        options = {'OutputFlag': 1}
    ) as opt:
        result = opt.solve(i, tee = True, warmstart = False)

def highs_solver():
    with pyo.SolverFactory(
        "appsi_highs"
    ) as opt:
        result = opt.solve(i, tee = True, warmstart = False)

def ipopt_solver():
    solver = pyo.SolverFactory(
        'ipopt',
        executable=str(idaes.bin_directory) + '/ipopt.exe'  # or just 'ipopt' on Linux/Mac
    )
    print(solver.available())
    return solver.solve(i, tee=True)

result = ipopt_solver()

from data_out.visualize_results import visualize
visualize(i, case, output_path="results/acopf_visualization.html")

...