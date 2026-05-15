from typing import List, Dict, Tuple, Union
import pandas as pd
import itertools as it
import numpy as np
import operator as op
from functools import reduce

def filter_df(df: object, conditions: list[list], operator: str = None):
    """
    Filter a dataframe based one or more conditions.
    
    :df: Dataframe to be filtered
    :conditions: Conditions to filter for in format [['column', 'comparator', 'value'],[...],...]
    :operator: Operation to combine conditions. Allows None (if only one condition), "AND", "OR" or "XOR".
    """

    supported_operators = ["AND", "OR", "XOR", None]
    supported_conditions = ['==', '!=', '>=', '>', '<=', '<']

    condition_lookup = {'==': op.eq,
                        '!=': op.ne,
                        '>=': op.ge,
                        '>': op. gt,
                        '<=': op.le,
                        '<': op. lt,}
    
    operator_lookup = {
        "AND": op.and_,
        "OR": op.or_,
        "XOR": op.xor,
    }

    #Check if correctly input
    if len(conditions) > 1 and operator == None:
        raise ValueError(f"More than 1 condition is defined, however no operator (e.g. AND, OR, XOR) has been defined")
    if len(conditions) == 1 and operator != None:
        raise ValueError(f"An operator has been defined, however only 1 condition is defined. Either specify > 1 condition, or remove the operator")

    filter_mask = []

    for column, condition, value in conditions:
        #Error Checking for parameter and conditional filter
        if column not in df.columns:
            raise KeyError(f"Parameter '{column}' not found in '{df}' columns")
        if condition not in condition_lookup:
            raise KeyError(f"Filter condition '{condition}' is not defined for this function. Please use one of {supported_conditions}")

        #If only one condition is defined, then use this as single mask for the df
        if len(conditions) == 1:
            return df.loc[condition_lookup[condition](df[column],value)]
        else:
        #Append condition to filter mask
            filter_mask.append(condition_lookup[condition](df[column],value))

    #Check selected operator is a supported operation
    if operator not in supported_operators:
        raise ValueError(f"The operator {operator} is not defined for this function. Please use one of {supported_operators}")
    
    if operator is None:
        return df.loc

    return df.loc[reduce(operator_lookup[operator], filter_mask)]


def df_to_scaled_param_dict(df:object, index:str , param: float, scalar: float) -> Dict[str, float]:
    '''Return a dict mapping the index (e.g. generator name) to parameter scaled against baseMVA'''

    #Check parameters exist in df
    for param in [index,param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in df data")

    #Filter df and return dictionary
    return df.set_index(index)[param].mul(scalar).round(6).to_dict()

def df_to_scaled_param_list(case: object, component: str, param: float, scalar: float) -> List[float]:
    '''Return a list mapping the index (e.g. generator name) to parameter scaled against baseMVA'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    if param not in df.columns:
        raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    
    #Filter df and return list
    return df[param].mul(scalar).round(6).to_list()

def df_to_param_list(case: object, component: str, param: Union[str,float,int]) -> List[Union[str, float, int]]:
    '''Return list of components, optionally filtered by a parameter'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    if param not in df.columns:
        raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Filter df and return list
    return df[param].to_list()
    
def df_to_param_dict(df:object, index: str, param: Union[str,float,int]) -> Dict[List[Union[str, float, int]], Union[str, float, int]]:
    '''Return list of components filtered by a parameter'''

    #Check parameters exist in df
    for param in [index, param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in df data")

    #Filter df and return list
    return df.set_index(index)[param].to_dict()
        
def df_merge_to_dict(key_df: object, key_param: str, val_df: object, val_param: str, merge_param: str,) -> Dict[str, List[str]]:
    '''
    Function creates a map of one type of components (val) against another type of component (key). It produces a dict
    with the key_param as the key (e.g. bus), with the value being a list of all val_param (e.g. generators) that have been identified
    as belonging to the key_component by the merge_param (e.g. bus_name in the generators spreadsheet).

    Parameters
    ----------
    case: case object
    key_df: dataframe containint the parameter that should be mapped against
    key_param: key_component parameter that should form keys of the dictionary
    val_df: datafrane that should be mapped against the key_param
    val_param: val_component parameter that will form lists of values in the dictionary
    val_key_param: val_component parameter that links val_components to key_param (column on which merge is made)
    '''

    #Check parameters exist in key_component
    if key_param not in key_df.columns:
        raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    #Check parameters exist in val_component
    for param in [val_param, merge_param]:
        if param not in val_df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Perform mapping and return list
    key_component_map = val_df.groupby(merge_param)[val_param].apply(list).to_dict()
    for component in key_df[key_param]:
        key_component_map.setdefault(component, [])
    
    return key_component_map

def df_comma_param_to_list(df: object, comma_param: str) -> List[Union[str, float, int]]:
    '''
    Used to split a comma separated parameter into tuples,
    and return a dictionary of the component against an index
    '''
    
    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in dataframe data")

    #Filter df and return list
    return df[comma_param]\
                .dropna()\
                .str.split(',')\
                .explode()\
                .str.strip()\
                .unique()\
                .tolist()

def df_comma_param_to_dict(df: object, index: str, comma_param: str) -> Dict[str, tuple]:
    '''
    Used to split a comma separated parameter into tuples,
    and return a dictionary of the component against an index
    '''

    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in dataframe data")
         
    return df.set_index(index)[comma_param]\
            .dropna()\
            .apply(lambda x: tuple(groups.strip() for groups in x.split(',')))\
            .to_dict()

def df_comma_param_as_index_to_dict(case: object, component: str, val_param: str, comma_param: str) -> Dict[str, tuple]:
    '''
    Used to split a comma separated parameter into tuples, and return a dictionary with the comma_param as the index and val_param as values
    '''
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    df = getattr(case, component)

    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in '{component}' data")
           
    return df\
                    .assign(**{comma_param: df[comma_param].str.split(r",\s*")})\
                    .explode(comma_param)\
                    .assign(**{comma_param: lambda df: df[comma_param].str.strip()})\
                    .groupby(comma_param)[val_param]\
                    .apply(list)\
                    .to_dict()

def df_to_ordered_groupwise_combinations(df: object, index: str, group_param: str, ordered_param: str, r: int = 2) -> List[tuple]:
    '''
    Used to create ordered groupwise combinations of a parameter.
    '''

    #Check parameters exist in df
    for param in [group_param, ordered_param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in dataframe data")
        
    sorted_lifo_groups = df.sort_values([group_param, ordered_param])
    grouped_lifo_tuple_dict = sorted_lifo_groups.groupby('lifo_groups')['name'].apply(lambda x: list(it.combinations(x,r))).to_dict()
    # lifo_pairs_list = [lifo_pair_tuple for lifo_pairs_list in grouped_lifo_tuple_lists for lifo_pair_tuple in lifo_pairs_list]
        
    return grouped_lifo_tuple_dict

def df_to_zipped_param_list(df: object, index: str, zip_params: list) -> Dict[str,tuple]:
    '''Return list of components filtered by a parameter'''

    #Check parameters exist in df
    for param in zip_params:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in df data")

    return dict(zip(df[index] , zip(*(df[param] for param in zip_params))))

def df_to_zipped_mapped_param_list(
    df: object,
    index: str,
    zip_params: List[str],
    lookup_df: object,
    lookup_key: str,
    lookup_val: str,
) -> Dict[str, list]:
    '''
    Like df_to_zipped_param_list, but maps each zipped parameter value through a lookup dataframe.

    Parameters
    ----------
    df         : primary dataframe (e.g. branches)
    index      : column to use as dict keys (e.g. "name")
    zip_params : columns whose values are mapped via the lookup (e.g. ["from_busname", "to_busname"])
    lookup_df  : dataframe containing the mapping (e.g. busses)
    lookup_key : column in lookup_df to match against (e.g. "name")
    lookup_val : column in lookup_df whose value replaces the original (e.g. "zone")

    Example
    -------
    BRANCH_ZONES = df_to_zipped_mapped_param_list(
        case.branches, "name", ["from_busname", "to_busname"],
        case.busses, "name", "zone"
    )
    # → {"Branch1": ("ZoneA", "ZoneB"), ...}
    '''

    for param in zip_params:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in df data")
    if lookup_key not in lookup_df.columns:
        raise KeyError(f"Parameter '{lookup_key}' not found in lookup_df data")
    if lookup_val not in lookup_df.columns:
        raise KeyError(f"Parameter '{lookup_val}' not found in lookup_df data")

    lookup = lookup_df.set_index(lookup_key)[lookup_val].to_dict()

    return {k: list(v) for k, v in zip(
        df[index],
        zip(*(df[param].map(lookup) for param in zip_params))
    )}

def df_to_paired_params_list(df: object, param_1, param_2, param_2_comma = False):
    '''Return a list of pairs of all parameters'''

    #Check parameters exist in df
    for param in [param_1, param_2]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in 'dataframe")   
    
    #Get Dictionary
    if param_2_comma == True:
        dictionary = df_comma_param_to_dict(df, param_1, param_2)
    else:
        dictionary = df_to_param_dict(df, param_1, param_2)
    
    #Flatten List
    return [(param_1, param_2_item) for param_1, param_2 in dictionary.items() for param_2_item in param_2]

def df_series_param_index_list(df, timestep, filter_operation = None, filter_value = None) -> list:
    #~~~~~~# Defining Filter Operations and Error Checking #~~~~~#
    #Define supported operations
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    #Check that all filters are set if one is set.
    if any(param is None for param in [filter_operation, filter_value]) and not all(param is None for param in [filter_operation, filter_value]):
        raise ValueError("If any of filter_operation or filter_value is set, all must be provided.")

    #Check selected operator is a supported operation
    if filter_operation not in supported_operations:
        raise ValueError(f"The operator {filter_operation} is not defined for this function. Please use one of {supported_operations}")

    #If no filter_operation then just return the headline index
    if filter_operation is None:
        return list(df.columns)
    #Else get a filtered list of the index
    else:
        if filter_operation == '=':
            return list(df.stack().loc[timestep].loc[lambda x: x == filter_value].index)
        elif filter_operation == '!=':
            return list(df.stack().loc[timestep].loc[lambda x: x != filter_value].index)
        elif filter_operation == '>=':
            return list(df.stack().loc[timestep].loc[lambda x: x >= filter_value].index)
        elif filter_operation == '>':
            return list(df.stack().loc[timestep].loc[lambda x: x > filter_value].index)
        elif filter_operation == '<=':
            return list(df.stack().loc[timestep].loc[lambda x: x <= filter_value].index)
        elif filter_operation == '<':
            return list(df.stack().loc[timestep].loc[lambda x: x < filter_value].index)
        else:
            raise ValueError(f"Unsupported operation '{filter_operation}'")   

def get_scaled_ts_param_dict(df, timestep, scalar: float) -> list:
    return (df.stack().loc[timestep]*scalar.round(6)).to_dict()

def get_ts_param_index_list(df, timestep, filter_operation = None, filter_value = None) -> list:
   
    #~~~~~~# Defining Filter Operations and Error Checking #~~~~~#
    #Define supported operations
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    #Check that all filters are set if one is set.
    if any(param is None for param in [filter_operation, filter_value]) and not all(param is None for param in [filter_operation, filter_value]):
        raise ValueError("If any of filter_operation or filter_value is set, all must be provided.")

    #Check selected operator is a supported operation
    if filter_operation not in supported_operations:
        raise ValueError(f"The operator {filter_operation} is not defined for this function. Please use one of {supported_operations}")

    #If no filter_operation then just return the headline index
    if filter_operation is None:
        return list(df.columns)
    #Else get a filtered list of the index
    else:
        if filter_operation == '=':
            return list(df.stack().loc[timestep].loc[lambda x: x == filter_value].index)
        elif filter_operation == '!=':
            return list(df.stack().loc[timestep].loc[lambda x: x != filter_value].index)
        elif filter_operation == '>=':
            return list(df.stack().loc[timestep].loc[lambda x: x >= filter_value].index)
        elif filter_operation == '>':
            return list(df.stack().loc[timestep].loc[lambda x: x > filter_value].index)
        elif filter_operation == '<=':
            return list(df.stack().loc[timestep].loc[lambda x: x <= filter_value].index)
        elif filter_operation == '<':
            return list(df.stack().loc[timestep].loc[lambda x: x < filter_value].index)
        else:
            raise ValueError(f"Unsupported operation '{filter_operation}'")   



def get_ts_param_dict(df, timestep) -> list:
    return (df.stack().loc[timestep]).to_dict()



def df_merge_filter_to_list(
    df: object,
    merge_df: object,
    merge_df_cols: List[str],
    left_on: str,
    right_on: str,
    return_param: str,
    conditions: list[list],
    operator: str = None
) -> List[str]:
    '''
    Merge df against merge_df and return a filtered list of return_param values.

    Parameters
    ----------
    df            : primary dataframe (e.g. generators)
    merge_df      : dataframe to merge against (e.g. busses)
    merge_df_cols : columns to retain from merge_df before merging (e.g. ['name', 'zone'])
    left_on       : column in df to join on
    right_on      : column in merge_df to join on
    return_param  : column in the merged dataframe whose values form the returned list
    conditions    : filter conditions in format [['column', 'comparator', 'value'], ...]
    operator      : how to combine multiple conditions — None, "AND", "OR", or "XOR"
    '''

    supported_operators = ["AND", "OR", "XOR", None]
    supported_conditions = ['==', '!=', '>=', '>', '<=', '<']

    condition_lookup = {'==': op.eq, '!=': op.ne, '>=': op.ge,
                        '>': op.gt, '<=': op.le, '<': op.lt}
    operator_lookup  = {'AND': op.and_, 'OR': op.or_, 'XOR': op.xor}

    if len(conditions) > 1 and operator is None:
        raise ValueError("More than 1 condition defined but no operator (AND, OR, XOR) provided.")
    if len(conditions) == 1 and operator is not None:
        raise ValueError("An operator was provided but only 1 condition is defined.")
    if operator not in supported_operators:
        raise ValueError(f"Operator '{operator}' is not supported. Use one of {supported_operators}.")

    merged = (
        df.merge(
            merge_df[merge_df_cols],
            how='inner',
            left_on=left_on,
            right_on=right_on,
            suffixes=('', '_drop')
        )
        .drop(columns=[c for c in df.columns if c.endswith('_drop')], errors='ignore')
    )

    for column, condition, _ in conditions:
        if column not in merged.columns:
            raise KeyError(f"Column '{column}' not found in merged dataframe.")
        if condition not in condition_lookup:
            raise KeyError(f"Condition '{condition}' is not supported. Use one of {supported_conditions}.")

    if len(conditions) == 1:
        column, condition, value = conditions[0]
        return merged.loc[condition_lookup[condition](merged[column], value)][return_param].tolist()

    filter_mask = [condition_lookup[cond](merged[col], val) for col, cond, val in conditions]
    return merged.loc[reduce(operator_lookup[operator], filter_mask)][return_param].tolist()

