import sys
sys.path.insert(1, 'C:\\Users\\richn\\OneDrive - University of Strathclyde\\General - EEE_STU_NayerPhD\\#CODEZONE\\oats_v2')

from pyomo.environ import *
import pandas as pd
from utils.df_utils import *
from oats.data_io import load_case
from typing import List, Dict, Tuple, Union

m = AbstractModel()
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
            'col_types': {'name': pd.StringDtype(), #Bus Name
                            'baseKV': float, #Base kV for Bus
                            'type': int, #Type of Bus
                            'zone': pd.StringDtype(), #Bus Zone
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
                            'ContinousRating': int #Line Continuous Rating [MVA]
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
                            'ContinousRating': int #Transformer Continuous Rating [MVA]
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
                            'type': pd.StringDtype(), #Generator Type
                            'PGMINGEN': float, #Minimum Real Power Generation [MW]
                            'PGLB': float, #Generator Real Power Lower Bound [MW]
                            'PGUB': float, #Generator Real Power Upper Bound [MW]
                            'FuelType': pd.StringDtype(), #Generator Fuel Type
                            'synchronous': pd.StringDtype(), #Generator Synchronous Status (Yes/No)
                            'costc1': float, #Generator Variable Cost [£/MWh]
                            'costc0': float, #Generator Fixed Cost [£]
                            'bid': float, #Generator Bid Cost [£/MWh]
                            'offer': float #Generator Offer Cost [£/MWh]
            },
            'dropna': True,
            'filter_active': True
        },
        # ── baseMVA Excel Sheet ──────────────────────────────────────────────────────────
        'baseMVA': {
            'key': 'baseMVA',
            'col_types': {'baseMVA': float}, #System Base MVA [MVA]
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
        # ── Power Line Maximum Real Power Flow [MW] (Rows = Timesteps, Columns = Branch Name) ──────────────────────────────────────────────────────────
        'ts_Lmax': {
            'key': 'ts_Lmax',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Transformer Maximum Real Power Flow [MW] (Rows = Timesteps, Columns = Transformer Name) ──────────────────────────────────────────────────────────
        'ts_TLmax': {
            'key': 'ts_TLmax',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Generator Minimum Real Power Out [MW] (Rows = Timesteps, Columns = Generator Name) ──────────────────────────────────────────────────────────
        # 'ts_PGMINGEN': {
        #     'key': 'ts_PGMINGEN',
        #     'index': 'timestep',
        #     'dropna': True,
        #     'filter_active': True
        # },
        # ── Generator Real Power Lower Bound [MW] (Rows = Timesteps, Columns = Generator Name) ──────────────────────────────────────────────────────────
        'ts_PGLB': {
            'key': 'ts_PGLB',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Generator Real Power Upper Bound [MW] (Rows = Timesteps, Columns = Generator Name) ──────────────────────────────────────────────────────────
        'ts_PGUB': {
            'key': 'ts_PGUB',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # ── Generator Bid Price [£/MWh] (Rows = Timesteps, Columns = Generator Name) ──────────────────────────────────────────────────────────
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
        i.BUSSES = Set(initialize = BUS_NAMES)

        # ── Slack Bus [Slackbus_name] ──────────────────────────────────────────────────────────
        SLACK_BUS = filter_df(case.busses, [['type', '==', 3]])['name'].to_list()
        i.SLACK_BUS = Set(initialize = SLACK_BUS)

    def generation_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Generator Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generator Names [Generator1_name, Generator2_name,...] ──────────────────────────────────────────────────────────
        GENERATOR_NAMES = case.generators['name'].to_list()
        i.GENERATORS = Set(initialize = GENERATOR_NAMES)

        # ── Generators Indexed to Busses (Dict: {Bus: [Gen1, Gen2, ...]}) ──────────────────────────────────────────────────────────
        GENERATORS_AT_BUSSES = df_merge_to_dict(case.busses, "name", case.generators, "name","busname")
        i.GENERATORS_AT_BUSSES = Set(i.BUSSES, initialize = GENERATORS_AT_BUSSES)

    def branch_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Branch Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Branch Names [Branch1_name, Branch2_name,...] ──────────────────────────────────────────────────────────
        BRANCH_NAMES = case.branches['name'].to_list()
        i.BRANCHES = Set(initialize = BRANCH_NAMES)

        # ── Branches To_Bus Indexed to Busses (Dict: {Bus: [Branch1, Branch2,...]}) ──────────────────────────────────────────────────────────
        BUS_BRANCHES_IN = df_merge_to_dict(case.busses, "name", case.branches, "name", "to_busname")
        i.BUS_BRANCHES_IN = Set(i.BUSSES, initialize = BUS_BRANCHES_IN)

        # ── Branches From_Bus Indexed to Busses (Dict: {Bus: [Branch1, Branch2,...]}) ──────────────────────────────────────────────────────────
        BUS_BRANCHES_OUT = df_merge_to_dict(case.busses, "name", case.branches, "name", "from_busname")
        i.BUS_BRANCHES_OUT = Set(i.BUSSES, initialize = BUS_BRANCHES_OUT)

        # ── Busses Indexed to Branches (Dict: {Branch: [(From_Bus, To_Bus),...]}) ──────────────────────────────────────────────────────────
        BRANCH_BUSSES = df_to_zipped_param_list(case.branches, "name", ["from_busname", "to_busname"])
        i.BRANCH_BUSSES = Set(i.BRANCHES, initialize = BRANCH_BUSSES, ordered = True)

    def transformer_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Transformer Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Set of Transformer Names [Transformer1_name, Transformer2_name,...] ──────────────────────────────────────────────────────────
        TRANSFORMER_NAMES = case.transformers['name'].to_list()
        i.TRANSFORMERS = Set(initialize = TRANSFORMER_NAMES)

        # ── Set of Transformer To_Bus Indexed to Busses (Dict: {Bus: [Transformer1, Transformer2,...]}) ──────────────────────────────────────────────────────────
        BUS_TRANSFORMERS_IN = df_merge_to_dict(case.busses, "name", case.transformers, "name", "to_busname")
        i.BUS_TRANSFORMERS_IN = Set(i.BUSSES, initialize = BUS_TRANSFORMERS_IN)

        # ── Set of Transformer From_Bus Indexed to Busses (Dict: {Bus: [Transformer1, Transformer2,...]}) ──────────────────────────────────────────────────────────
        BUS_TRANSFORMERS_OUT = df_merge_to_dict(case.busses, "name", case.transformers, "name", "from_busname")
        i.BUS_TRANSFORMERS_OUT = Set(i.BUSSES, initialize = BUS_TRANSFORMERS_OUT)

        # ── Set of Busses Indexed to Transformers (Dict: {Transformer: [(From_Bus, To_Bus),...]}) ──────────────────────────────────────────────────────────
        TRANSFORMER_BUSSES = df_to_zipped_param_list(case.transformers, "name", ["from_busname", "to_busname"])
        i.TRANSFORMER_BUSSES = Set(i.TRANSFORMERS, initialize = TRANSFORMER_BUSSES, ordered = True)

    def demand_sets():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Demand Sets
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Set of Demands [Demand1_name, Demand2_name,...] ──────────────────────────────────────────────────────────
        DEMAND_NAMES = case.demands['name'].to_list()
        i.DEMANDS = Set(initialize = DEMAND_NAMES)

        # ── Set of Negative Real Power Demands [NegativeDemand1_name, NegativeDemand2_name,...] ──────────────────────────────────────────────────────────
        DEMANDS_NEGATIVE_REAL = filter_df(case.demands, [['real', '<', 0]])
        i.DEMANDS_NEGATIVE_REAL = Set(initialize = DEMANDS_NEGATIVE_REAL)

        # ── Set of Demands Indexed to Busses (Dict: {Bus: [Demand1, Demand2,...]}) ──────────────────────────────────────────────────────────
        BUS_DEMANDS =  df_merge_to_dict(case.busses, 'name', case.demands, 'name', 'busname')
        i.BUS_DEMANDS = Set(i.BUSSES, initialize = BUS_DEMANDS)

    # ── Assign Sets to Model ──────────────────────────────────────────────────────────────────
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
        # ── Branch Real Power Max (Continuous) [p.u.] Assumes MW input ──────────────────────────────────────────────────────────
        Branch_Real_Power_Max_Continuous = df_to_scaled_param_dict(case.branches, 'name', 'ContinuousRating', (1/case.baseMVA))
        i.Branch_Real_Power_Max_Continuous = Param(i.BRANCHES, domain = NonNegativeReals, initialize = Branch_Real_Power_Max_Continuous)

        # ── Branch Susceptance B [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Branch_Susceptance = df_to_param_dict(case.branches, 'name', 'b')
        i.Branch_Susceptance = Param(i.BRANCHES, domain = Reals, initialize = Branch_Susceptance)

        # ── Branch Reactance X [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Branch_Reactance = df_to_param_dict(case.branches, 'name', 'x')
        i.Branch_Reactance = Param(i.BRANCHES, domain = Reals, initialize = Branch_Reactance)

    def transformer_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Transformer Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Transformer Real Power Max (Continuous) [p.u.] Assumes MW input ──────────────────────────────────────────────────────────
        Transformer_Real_Power_Max_Continuous = df_to_scaled_param_dict(case.transformers, 'name', 'ContinuousRating', (1/case.baseMVA))
        i.Transformer_Real_Power_Max_Continuous = Param(i.TRANSFORMERS, domain = NonNegativeReals, initialize = Transformer_Real_Power_Max_Continuous)

        # ── Transformer Susceptance B [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Transformer_Susceptance = df_to_param_dict(case.transformers, 'name', 'b')
        i.Transformer_Susceptance = Param(i.TRANSFORMERS, domain = Reals, initialize = Transformer_Susceptance)

        # ── Transformer Reactance X [p.u.] Assumes p.u. input ──────────────────────────────────────────────────────────
        Transformer_Reactance = df_to_param_dict(case.transformers, 'name', 'x')
        i.Transformer_Reactance = Param(i.TRANSFORMERS, domain = Reals, initialize = Transformer_Reactance)

    def demand_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Demand Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Real Power Demand [p.u.] Assumes MW input ──────────────────────────────────────────────────────────
        Real_Power_Demand = df_to_scaled_param_dict(case.demands, 'name', 'real', (1/case.baseMVA))
        i.Real_Power_Demand = Param(i.DEMANDS, domain = Reals, initialize = Real_Power_Demand)

        # ── Value of Lost Load [£/MWh] ──────────────────────────────────────────────────────────
        Voll = df_to_param_dict(case.demands, 'name', 'VOLL')
        i.Voll = Param(i.DEMANDS, domain = Reals, initialize = Voll)

    def generator_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Generator Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generator Real Power Output Max [p.u.] Assumes MW input ──────────────────────────────────────────────────────────
        Gen_Real_Power_Max = df_to_scaled_param_dict(case.generators, 'name', 'PGUB', (1/case.baseMVA))
        i.Gen_Real_Power_Max = Param(i.GENERATORS, domain = Reals, initialize = Gen_Real_Power_Max)

        # ── Generator Real Power Output Min [p.u.] Assumes MW input ──────────────────────────────────────────────────────────
        Gen_Real_Power_Min = df_to_scaled_param_dict(case.generators, 'name', 'PGLB', (1/case.baseMVA))
        i.Gen_Real_Power_Min = Param(i.GENERATORS, domain = Reals, initialize = Gen_Real_Power_Min)

        # ── Generator Fixed Cost [£] ──────────────────────────────────────────────────────────
        Gen_Price_c0 = df_to_param_dict(case.generators, 'name', 'costc0')
        i.Gen_Price_c0 = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_c0)

        # ── Generator Variable Cost [£/MWh] ──────────────────────────────────────────────────────────
        Gen_Price_c1 = df_to_param_dict(case.generators, 'name', 'costc1')
        i.Gen_Price_c1 = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_c1)

        # ── Generator Bid Price [£/MWh] ──────────────────────────────────────────────────────────
        Gen_Price_Bid = df_to_param_dict(case.generators, 'name', 'bid')
        i.Gen_Price_Bid = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_Bid)

        # ── Generator Offer Price [£/MWh] ──────────────────────────────────────────────────────────
        Gen_Price_Offer = df_to_param_dict(case.generators, 'name', 'offer')
        i.Gen_Price_Offer = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_Offer)

    def system_parameters():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Per Unit System Parameters
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── System Base MVA [MVA] ──────────────────────────────────────────────────────────
        i.BaseMVA = Param(domain = Reals, initialize = case.baseMVA)

    # ── Call Functions to Create Parameters ──────────────────────────────────────────────────────────
    branch_parameters()
    transformer_parameters()
    demand_parameters()
    generator_parameters()
    system_parameters()
# ──────────────────────────────────────────────────────────────────────────────────────────


def initialise_variables():
# ──────────────────────────────────────────────────────────────────────────────────────────
# Initialise Variables
# ──────────────────────────────────────────────────────────────────────────────────────────
    def generator_variables():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Generator Variables
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generator Unit Commitment Status (Binary: 0 = Off, 1 = On) ──────────────────────────────────────────────────────────
        i.generator_commitment = Var(i.GENERATORS, domain = Binary)
        # ── Generator Real Power Output [p.u.] ──────────────────────────────────────────────────────────
        i.generator_real_power_out = Var(i.GENERATORS, domain = Reals)
        # ── Generator Real Power Bid [p.u.] ──────────────────────────────────────────────────────────
        i.generator_real_power_bid = Var(i.GENERATORS, domain = NonNegativeReals)
        # ── Generator Real Power Offer [p.u.] ──────────────────────────────────────────────────────────
        i.generator_real_power_offer = Var(i.GENERATORS, domain = NonNegativeReals)

    def demand_variables():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Demand Variables
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Real Power Demand Met [p.u.] ──────────────────────────────────────────────────────────
        i.demand_real_power_met = Var(i.DEMANDS, domain=Reals)
        # ── Proportion of Real Power Demand Met [0, 1] ──────────────────────────────────────────────────────────
        i.demand_proportion_real_power_met = Var(i.DEMANDS, domain = NonNegativeReals, bounds = (0,1))

    def branch_variables():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Branch Variables
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Branch Voltage Angle Difference [rad] ──────────────────────────────────────────────────────────
        i.branch_voltage_angle_difference = Var(i.BRANCHES, domain = Reals)
        # ── Branch Real Power Flow [p.u.] ──────────────────────────────────────────────────────────
        i.branch_real_power_flow = Var(i.BRANCHES, domain = Reals)

    def transformer_variables():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Transformer Variables
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Transformer Voltage Angle Difference [rad] ──────────────────────────────────────────────────────────
        i.transformer_voltage_angle_difference = Var(i.TRANSFORMERS, domain = Reals)
        # ── Transformer Real Power Flow [p.u.] ──────────────────────────────────────────────────────────
        i.transformer_real_power_flow = Var(i.TRANSFORMERS, domain = Reals)

    def bus_variables():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    #  Bus Variables
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Bus Voltage Angle [rad] ──────────────────────────────────────────────────────────
        i.bus_voltage_angle = Var(i.BUSSES, domain = Reals)

    # ── Call Functions to Assign Variables to Model ──────────────────────────────────────────────────────────
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
        # ── KCL Real Power Constraint (Nodal Power Balance) ──────────────────────────────────────────────────────────
        @i.Constraint(i.BUSSES)
        def KCL_DCOPF_constraint(i, bus):
            return + sum(i.generator_real_power_out[generator] for generator in i.GENERATORS_AT_BUSSES[bus])\
                   - sum(i.branch_real_power_flow[line] for line in i.BUS_BRANCHES_OUT[bus])\
                   + sum(i.branch_real_power_flow[line] for line in i.BUS_BRANCHES_IN[bus])\
                   - sum(i.transformer_real_power_flow[transformer] for transformer in i.BUS_TRANSFORMERS_OUT[bus])\
                   + sum(i.transformer_real_power_flow[transformer] for transformer in i.BUS_TRANSFORMERS_IN[bus])\
                   ==\
                   + sum(i.demand_real_power_met[demand] for demand in i.BUS_DEMANDS[bus])

        # ── KVL Branch Real Power Flow Constraint (DC Approximation: P = (1/X) * Δθ) ──────────────────────────────────────────────────────────
        @i.Constraint(i.BRANCHES)
        def branch_KVL_DCOPF(i, branch):
            return i.branch_real_power_flow[branch] == (1 / i.Branch_Reactance[branch]) * i.branch_voltage_angle_difference[branch]

        # ── Branch Voltage Angle Difference Constraint (Δθ = θ_from - θ_to) ──────────────────────────────────────────────────────────
        @i.Constraint(i.BRANCHES)
        def branch_voltage_angle(i,branch):
            return i.branch_voltage_angle_difference[branch] == + i.bus_voltage_angle[i.BRANCH_BUSSES[branch].at(1)] - i.bus_voltage_angle[i.BRANCH_BUSSES[branch].at(2)]

        # ── KVL Transformer Real Power Flow Constraint (DC Approximation: P = (1/X) * Δθ) ──────────────────────────────────────────────────────────
        @i.Constraint(i.TRANSFORMERS)
        def transformer_KVL_DCOPF(i, transformer):
            return i.transformer_real_power_flow[transformer] == (1 / i.Transformer_Reactance[transformer]) * i.transformer_voltage_angle_difference[transformer]

        # ── Transformer Voltage Angle Difference Constraint (Δθ = θ_from - θ_to) ──────────────────────────────────────────────────────────
        @i.Constraint(i.TRANSFORMERS)
        def transformer_voltage_angle(i,transformer):
            return i.transformer_voltage_angle_difference[transformer] == + i.bus_voltage_angle[i.TRANSFORMER_BUSSES[transformer].at(1)] - i.bus_voltage_angle[i.TRANSFORMER_BUSSES[transformer].at(2)]

        # ── Reference Bus Voltage Angle Constraint (θ_slack = 0) ──────────────────────────────────────────────────────────
        @i.Constraint(i.BUSSES)
        def voltage_ref_bus(i,bus):
            ref_bus = filter_df(case.busses, [['type', '==', 3]])['name'].to_list()
            if bus in ref_bus:
                return i.bus_voltage_angle[bus] == 0
            else:
                return Constraint.Skip

        # ── Branch Real Power Flow Upper Bound Constraint ──────────────────────────────────────────────────────────
        @i.Constraint(i.BRANCHES)
        def branch_real_power_flow_UB(i, branch):
            return i.branch_real_power_flow[branch] <= i.Branch_Real_Power_Max_Continuous[branch]

        # ── Branch Real Power Flow Lower Bound Constraint (Reverse Flow) ──────────────────────────────────────────────────────────
        @i.Constraint(i.BRANCHES)
        def branch_real_power_flow_UB_reverse(i, branch):
            return i.branch_real_power_flow[branch] >= -i.Branch_Real_Power_Max_Continuous[branch]

        # ── Transformer Real Power Flow Upper Bound Constraint ──────────────────────────────────────────────────────────
        @i.Constraint(i.TRANSFORMERS)
        def transformer_real_power_flow_UB(i, transformer):
            return i.transformer_real_power_flow[transformer] <= i.Transformer_Real_Power_Max_Continuous[transformer]

        # ── Transformer Real Power Flow Lower Bound Constraint (Reverse Flow) ──────────────────────────────────────────────────────────
        @i.Constraint(i.TRANSFORMERS)
        def transformer_real_power_flow_UB_reverse(i, transformer):
            return i.transformer_real_power_flow[transformer] >= -i.Transformer_Real_Power_Max_Continuous[transformer]


    def demand_constraints():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Demand Constraints
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Real Power Demand Met Constraint (demand_met = proportion * total_demand) ──────────────────────────────────────────────────────────
        @i.Constraint(i.DEMANDS)
        def demand_real_power_constraint(i, demand):
            return  i.demand_real_power_met[demand] == i.demand_proportion_real_power_met[demand] * i.Real_Power_Demand[demand]

        # ── Negative Real Power Demands Always Fully Met (e.g. generation embedded in demand) ──────────────────────────────────────────────────────────
        negative_demands = filter_df(case.demands, [['real', '<', 0]])['name'].to_list()
        @i.Constraint(i.DEMANDS)
        def demand_always_meet_ngtve_demand(i, demand):
            if demand in negative_demands:
                return i.demand_proportion_real_power_met[demand] == 1
            else:
                return Constraint.Skip

    def generation_constraints():
    # ──────────────────────────────────────────────────────────────────────────────────────────
    # Generation Constraints
    # ──────────────────────────────────────────────────────────────────────────────────────────
        # ── Generator Real Power Output Lower Bound (Unit Commitment: P >= commitment * P_min) ──────────────────────────────────────────────────────────
        @i.Constraint(i.GENERATORS)
        def generation_UC_real_power_LB(i, gen):
            return i.generator_real_power_out[gen] >= i.generator_commitment[gen] * i.Gen_Real_Power_Min[gen]

        # ── Generator Real Power Output Upper Bound (Unit Commitment: P <= commitment * P_max) ──────────────────────────────────────────────────────────
        @i.Constraint(i.GENERATORS)
        def generation_UC_real_power_UB(i, gen):
            return i.generator_real_power_out[gen] <= i.generator_commitment[gen] * i.Gen_Real_Power_Max[gen]

    # ── Call Functions to Assign Constraints to Model ──────────────────────────────────────────────────────────
    network_constraints()
    demand_constraints()
    generation_constraints()
# ──────────────────────────────────────────────────────────────────────────────────────────


def objective_marginal_cost(i):
# ──────────────────────────────────────────────────────────────────────────────────────────
# Objective Function — Minimise Total Marginal Cost + Value of Lost Load
# ──────────────────────────────────────────────────────────────────────────────────────────
    rnd = np.random.default_rng(100)

    obj = sum((i.Gen_Price_c1[gen]+rnd.random())*i.generator_real_power_out[gen]+(i.generator_commitment[gen] * i.Gen_Price_c0[gen]/i.BaseMVA) for gen in i.GENERATORS) +\
        sum(i.Voll[demand]*(1-i.demand_proportion_real_power_met[demand])*i.Real_Power_Demand[demand] for demand in i.DEMANDS)
    return obj


# ── Import Case, Initialise Sets / Parameters / Variables / Constraints ──────────────────────────────────────────────────────────
case = import_case()
initialise_sets(case)
initialise_parameters(case)
initialise_variables()
initialise_constraints()

# ── Define Model Objective ──────────────────────────────────────────────────────────────────────────────────
i.obj = Objective(rule = objective_marginal_cost(i), sense = minimize)

# ── Solve Model ──────────────────────────────────────────────────────────────────────────────────
with SolverFactory(
    "gurobi",
    solver_io = "python",
    options = {'OutputFlag': 1}
) as opt:
    result = opt.solve(i, tee = True, warmstart = False)
...

