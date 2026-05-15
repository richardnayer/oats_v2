import sys
sys.path.insert(1, 'C:\Users\richn\OneDrive - University of Strathclyde\General - EEE_STU_NayerPhD\#CODEZONE\oats_v2')

from pyomo.environ import *
import pandas as pd
from utils.df_utils import *
from data_io import load_case
from typing import List, Dict, Tuple, Union

m = AbstractModel()
i = m.create_instance()

def import_case():  
    testcase = "illustrative_testcase.xlsx"
    
    #Define Static Data to Import
    static_data_config: Dict[str, Dict[str, Any]] = {
        'bus': {
            'key': 'busses',
            'col_types': {'name': pd.StringDtype(),
                            'baseKV': float,
                            'type': int,
                            'zone': pd.StringDtype(),
            },
            'dropna': True,
            'filter_active': True
        },
        'demand': {
            'key': 'demands',
            'col_types': {'name': pd.StringDtype(),
                            'busname': pd.StringDtype(),
                            'real': float,
                            'stat': int,
                            'VOLL': int
            },
            'dropna': True,
            'filter_active': True
        },
        'branch': {
            'key': 'branches',
            'col_types': {'name': pd.StringDtype(),
                            'from_busname': pd.StringDtype(),
                            'to_busname': pd.StringDtype(),
                            'stat': int,
                            'r': float,
                            'x': float,
                            'b': float,
                            'ShortTermRating': int,
                            'ContinousRating': int 
            },
            'dropna': True,
            'filter_active': True
        },
        'transformer': {
            'key': 'transformers',
            'col_types': {'name': pd.StringDtype(),
                            'from_busname': pd.StringDtype(),
                            'to_busname': pd.StringDtype(),
                            'type': pd.StringDtype(),
                            'stat': int,
                            'r': float,
                            'x': float,
                            'b': float,
                            'ShortTermRating': int,
                            'ContinousRating': int
            },
            'dropna': True,
            'filter_active': True
        },
        'generator': {
            'key': 'generators',
            'col_types': {'busname': pd.StringDtype(),
                            'name': pd.StringDtype(),
                            'export_policy': pd.StringDtype(),
                            'lifo_group': pd.StringDtype(),
                            'lifo_position': pd.StringDtype(),
                            'prorata_groups': pd.StringDtype(),
                            'stat': int,
                            'type': pd.StringDtype(),
                            'PGMINGEN': float,
                            'PGLB': float,
                            'PGUB': float,
                            'FuelType': pd.StringDtype(),
                            'synchronous': pd.StringDtype(),
                            'costc1': float,
                            'costc0': float,
                            'bid': float,
                            'offer': float
            },
            'dropna': True,
            'filter_active': True
        },
        'baseMVA': {
            'key': 'baseMVA',
            'col_types': {'baseMVA': float},
            'dropna': True,
            'filter_active': False
        }
            }

    #Define Series Data to Import
    series_data_config: Dict[str, Dict[str, Any]] = {
        'ts_PD': {
            'key': 'ts_PD',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        'ts_VOLL': {
            'key': 'ts_VOLL',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        'ts_Lmax': {
            'key': 'ts_Lmax',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        'ts_TLmax': {
            'key': 'ts_TLmax',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        # 'ts_PGMINGEN': {
        #     'key': 'ts_PGMINGEN',
        #     'index': 'timestep',
        #     'dropna': True,
        #     'filter_active': True
        # },
        'ts_PGLB': {
            'key': 'ts_PGLB',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        'ts_PGUB': {
            'key': 'ts_PGUB',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        },
        'ts_bid': {
            'key': 'ts_bid',
            'index': 'timestep',
            'dropna': True,
            'filter_active': True,
            # 'col_types': {'timestep': pd.StringDtype(),}
        }
    }

    #Load Case
    case = load_case.Case()
    case._load_excel_case(testcase, static_data_config, series = True, series_config = series_data_config)
    return case

def initialise_sets(case):

    #Sets Related to Busses
    def bus_sets():
        BUS_NAMES = filter_df(case.busses, [['type', '!=', 0]])['name'].to_list()
        i.BUSSES = Set(initialize = BUS_NAMES)

        SLACK_BUS = filter_df(case.busses, [['type', '==', 3]])['name'].to_list()
        i.SLACK_BUS = Set(initialize = SLACK_BUS)
    
    #Sets Related to Generators
    def generation_sets():
        GENERATOR_NAMES = case.generators['name'].to_list()
        i.GENERATORS = Set(initialize = GENERATOR_NAMES)

        GENERATORS_AT_BUSSES = df_merge_to_dict(case.busses, "name", case.generators, "name","busname")
        i.GENERATORS_AT_BUSSES = Set(i.BUSSES, initialize = GENERATORS_AT_BUSSES)

    #Sets Related to Branches
    def branch_sets():
        BRANCH_NAMES = case.branches['name'].to_list()
        i.BRANCHES = Set(initialize = BRANCH_NAMES)

        BUS_BRANCHES_IN = df_merge_to_dict(case.busses, "name", case.branches, "name", "to_busname")
        i.BUS_BRANCHES_IN = Set(i.BUSSES, initialize = BUS_BRANCHES_IN)

        BUS_BRANCHES_OUT = df_merge_to_dict(case.busses, "name", case.branches, "name", "from_busname")
        i.BUS_BRANCHES_OUT = Set(i.BUSSES, initialize = BUS_BRANCHES_OUT)

        BRANCH_BUSSES = df_to_zipped_param_list(case.branches, "name", ["from_busname", "to_busname"])
        i.BRANCH_BUSSES = Set(i.BRANCHES, initialize = BRANCH_BUSSES, ordered = True)

    #Sets Related to Transformers
    def transformer_sets():
        TRANSFORMER_NAMES = case.transformers['name'].to_list()
        i.TRANSFORMERS = Set(initialize = TRANSFORMER_NAMES)

        BUS_TRANSFORMERS_IN = df_merge_to_dict(case.busses, "name", case.transformers, "name", "to_busname")
        i.BUS_TRANSFORMERS_IN = Set(i.BUSSES, initialize = BUS_TRANSFORMERS_IN)

        BUS_TRANSFORMERS_OUT = df_merge_to_dict(case.busses, "name", case.transformers, "name", "from_busname")
        i.BUS_TRANSFORMERS_OUT = Set(i.BUSSES, initialize = BUS_TRANSFORMERS_OUT)

        TRANSFORMER_BUSSES = df_to_zipped_param_list(case.transformers, "name", ["from_busname", "to_busname"])
        i.TRANSFORMER_BUSSES = Set(i.TRANSFORMERS, initialize = TRANSFORMER_BUSSES, ordered = True)

    #Sets Related to Demands
    def demand_sets():
        DEMAND_NAMES = case.demands['name'].to_list()
        i.DEMANDS = Set(initialize = DEMAND_NAMES)

        DEMANDS_NEGATIVE_REAL = filter_df(case.demands, [['real', '<', 0]])
        i.DEMANDS_NEGATIVE_REAL = Set(initialize = DEMANDS_NEGATIVE_REAL)

        BUS_DEMANDS =  df_merge_to_dict(case.busses, 'name', case.demands, 'name', 'busname')
        i.BUS_DEMANDS = Set(i.BUSSES, initialize = BUS_DEMANDS)


    #Call functions to create sets
    bus_sets()
    generation_sets()
    branch_sets()
    transformer_sets()
    demand_sets()

def initialise_parameters(case):

    def branch_parameters():
        Branch_Real_Power_Max_Continuous = df_to_scaled_param_dict(case.branches, 'name', 'ContinuousRating', (1/case.baseMVA))
        i.Branch_Real_Power_Max_Continuous = Param(i.BRANCHES, domain = NonNegativeReals, initialize = Branch_Real_Power_Max_Continuous)

        Branch_Susceptance = df_to_param_dict(case.branches, 'name', 'b')
        i.Branch_Susceptance = Param(i.BRANCHES, domain = Reals, initialize = Branch_Susceptance)

        Branch_Reactance = df_to_param_dict(case.branches, 'name', 'x')
        i.Branch_Reactance = Param(i.BRANCHES, domain = Reals, initialize = Branch_Reactance)

    def transformer_parameters():
        Transformer_Real_Power_Max_Continuous = df_to_scaled_param_dict(case.transformers, 'name', 'ContinuousRating', (1/case.baseMVA))
        i.Transformer_Real_Power_Max_Continuous = Param(i.TRANSFORMERS, domain = NonNegativeReals, initialize = Transformer_Real_Power_Max_Continuous)

        Transformer_Susceptance = df_to_param_dict(case.transformers, 'name', 'b')
        i.Transformer_Susceptance = Param(i.TRANSFORMERS, domain = Reals, initialize = Transformer_Susceptance)

        Transformer_Reactance = df_to_param_dict(case.transformers, 'name', 'x')
        i.Transformer_Reactance = Param(i.TRANSFORMERS, domain = Reals, initialize = Transformer_Reactance)

    def demand_parameters():
        Real_Power_Demand = df_to_scaled_param_dict(case.demands, 'name', 'real', (1/case.baseMVA))
        i.Real_Power_Demand = Param(i.DEMANDS, domain = Reals, initialize = Real_Power_Demand)

        Voll = df_to_param_dict(case.demands, 'name', 'VOLL')
        i.Voll = Param(i.DEMANDS, domain = Reals, initialize = Voll)
    
    def generator_parameters():
        Gen_Real_Power_Max = df_to_scaled_param_dict(case.generators, 'name', 'PGUB', (1/case.baseMVA))
        i.Gen_Real_Power_Max = Param(i.GENERATORS, domain = Reals, initialize = Gen_Real_Power_Max)

        Gen_Real_Power_Min = df_to_scaled_param_dict(case.generators, 'name', 'PGLB', (1/case.baseMVA))
        i.Gen_Real_Power_Min = Param(i.GENERATORS, domain = Reals, initialize = Gen_Real_Power_Min)

        Gen_Price_c0 = df_to_param_dict(case.generators, 'name', 'costc0')
        i.Gen_Price_c0 = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_c0)

        Gen_Price_c1 = df_to_param_dict(case.generators, 'name', 'costc1')
        i.Gen_Price_c1 = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_c1)

        Gen_Price_Bid = df_to_param_dict(case.generators, 'name', 'bid')
        i.Gen_Price_Bid = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_Bid)

        Gen_Price_Offer = df_to_param_dict(case.generators, 'name', 'offer')
        i.Gen_Price_Offer = Param(i.GENERATORS, domain = Reals, initialize = Gen_Price_Offer)

    def system_parameters():
        i.BaseMVA = Param(domain = Reals, initialize = case.baseMVA)


    #Call functions to create sets
    branch_parameters()
    transformer_parameters()
    demand_parameters()
    generator_parameters()
    system_parameters()

def initialise_variables():

    def generator_variables():
        i.generator_commitment = Var(i.GENERATORS, domain = Binary)
        i.generator_real_power_out = Var(i.GENERATORS, domain = Reals)
        i.generator_real_power_bid = Var(i.GENERATORS, domain = NonNegativeReals)
        i.generator_real_power_offer = Var(i.GENERATORS, domain = NonNegativeReals)

    def demand_variables():
        i.demand_real_power_met = Var(i.DEMANDS, domain=Reals)
        i.demand_proportion_real_power_met = Var(i.DEMANDS, domain = NonNegativeReals, bounds = (0,1))

    def branch_variables():
        i.branch_voltage_angle_difference = Var(i.BRANCHES, domain = Reals)
        i.branch_real_power_flow = Var(i.BRANCHES, domain = Reals)

    def transformer_variables():
        i.transformer_voltage_angle_difference = Var(i.TRANSFORMERS, domain = Reals)
        i.transformer_real_power_flow = Var(i.TRANSFORMERS, domain = Reals)
    
    def bus_variables():
        i.bus_voltage_angle_difference = Var(i.BUSSES, domain = Reals)
    
    generator_variables()
    demand_variables()
    branch_variables()
    transformer_variables()
    bus_variables()

def initialise_constraints():

    def network_constraints():
        @i.Constraint()
        def KCL_copperplate_constraint(i):
            return sum(i.generator_real_power_out[gen] for gen in i.GENERATORS) ==\
                sum(i.demand_real_power_met[demand] for demand in i.DEMANDS)

    def demand_constraints():
        @i.Constraint(i.DEMANDS)
        def demand_real_power_constraint(i, demand):
            return  i.demand_real_power_met[demand] == i.demand_proportion_real_power_met[demand] * i.Real_Power_Demand[demand]
        
        negative_demands = filter_df(case.demands, [['real', '<', 0]])['name'].to_list()
        @i.Constraint(i.DEMANDS)
        def demand_always_meet_ngtve_demand(i, demand):
            if demand in negative_demands:
                return i.demand_proportion_real_power_met[demand] == 1
            else:
                return Constraint.Skip
    
    def generation_constraints():
        @i.Constraint(i.GENERATORS)
        def generation_UC_real_power_min(i, gen):
            return i.generator_real_power_out[gen] >= i.generator_commitment[gen] * i.Gen_Real_Power_Min[gen]

        @i.Constraint(i.GENERATORS)
        def generation_UC_real_power_max(i, gen):
            return i.generator_real_power_out[gen] <= i.generator_commitment[gen] * i.Gen_Real_Power_Max[gen]

    network_constraints()
    demand_constraints()
    generation_constraints()   

def objective_copper_plate_marginal_cost(i):
    rnd = np.random.default_rng(100)

    obj = sum((i.Gen_Price_c1[gen]+rnd.random())*i.generator_real_power_out[gen]+(i.generator_commitment[gen] * i.Gen_Price_c0[gen]/i.BaseMVA) for gen in i.GENERATORS) +\
        sum(i.Voll[demand]*(1-i.demand_proportion_real_power_met[demand])*i.Real_Power_Demand[demand] for demand in i.DEMANDS)
    return obj


#Import Case, Initialise Sets/Params/Vars/Constraints
case = import_case()
initialise_sets(case)
initialise_parameters(case)
initialise_variables()
initialise_constraints()

#Define Model Objective
i.obj = Objective(rule = objective_copper_plate_marginal_cost(i), sense = minimize)

#Solve Model
with SolverFactory(
    "gurobi",
    solver_io = "python",
    options = {'OutputFlag': 1}
) as opt:
    result = opt.solve(i, tee = True, warmstart = False)
...

