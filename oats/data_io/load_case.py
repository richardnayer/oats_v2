"""
__authors__ = "Richard Nayer"
__credits__ = "University of Strathclyde"
__version__ = "0.0.1"
__status__ = "Prototype"
__description__ = "Load a case for analysis and modelling. Currently allows the loading of an excel sheet. Config is definedelsewhere."
"""

import logging
from collections import UserDict
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import oats.utils.df_utils as helpers

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Change to DEBUG for more details
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Case(UserDict):
    """
    A container for electrical system case data loaded from Excel.
    Allows dictionary-style and attribute-style access to components.
    """
    
    # ~~ HELPER FUNCTIONS
    def __getattr__(self, item: str) -> pd.DataFrame:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(f"'Case' object has no attribute '{item}'") from e

    def _filter_nonzero_stat(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[df['stat'] != 0] if 'stat' in df.columns else df

    def _apply_column_types(self, df: pd.DataFrame, col_types: Dict[str, type]) -> pd.DataFrame:
        for col, dtype in col_types.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except Exception as e:
                    raise ValueError(f"Error converting column '{col}' to {dtype}: {e}")
        return df
    
    def _set_baseMVA(self) -> float:
        if len(self.baseMVA['baseMVA']) > 1:
            raise Exception("More than one base MVA defined")
        
        self.baseMVA = self.baseMVA['baseMVA'][0]
        return None

    def summary(self) -> None:
        print("Case Summary:")
        for key, df in self.data.items():
            print(f" - {key}: {df.shape[0]} rows, {df.shape[1]} columns")

    # ~~ LOAD EXCEL CASE
    def _load_excel_case(self, filepath: str, static_config: Dict, series: bool = False, series_config: Dict = None) -> None:
        """
        Load system case data from an Excel file.
        Args:
            filepath (str): Path to the Excel file.
            static_config (Dict): Dictionary containing the config. for static data sheets to be loaded.
            series (bool): Whether to load series data.
            series_config (Dict): Dictionary containing the config. for series data sheets to be loaded.
        """

        # ~ Define filepath and check if filepath exists
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"Excel file not found: {filepath}")

        #{HF} Inner Helper Function to parse sheets defined in the config file
        def _sheet_parser(self, excel_file: pd.ExcelFile, sheet_config: Dict[str, Dict[str, str]]) -> None:
            #Parse all sheets into individual dataframes, according to config settings, add to 'self' object.
            for sheet_name, config in sheet_config.items():
                if sheet_name not in excel_file.sheet_names:
                    logger.warning(f"Sheet '{sheet_name}' not found in Excel file.")
                    continue

                logger.debug(f"Processing sheet: {sheet_name}")
                df = excel_file.parse(sheet_name)

                if config.get('dropna') != None:
                    df = df.dropna(how='all')

                if config.get('filter_active') != None:
                    df = self._filter_nonzero_stat(df)

                if config.get('col_types') != None:
                    df = self._apply_column_types(df, config['col_types'])

                if config.get('index') != None:
                    df = df.set_index(config.get('index'))
                
                #Round values to reduce solver RHS differences
                df = df.round(6)

                self[config['key']] = df
                logger.info(f"Loaded {len(df)} rows into '{config['key']}'")

        # ~ Open excel file, and parse all sheets in config
        logger.info(f"Loading Excel file: {filepath}")
        with pd.ExcelFile(filepath, engine='openpyxl') as excel_file:
            #Static Sheets
            _sheet_parser(self, excel_file, static_config)

            #Series Sheets (if True)
            if series:
                _sheet_parser(self, excel_file, series_config)
                self.series_index = self.ts_PD.index.to_list()
        logger.info(f"Excel file loaded: {filepath}")

        # Set Base MVA value based on sheet
        self._set_baseMVA()


# if __name__ == "__main__":
#     testcase = Case()
#     testcase._load_excel_case("end-to-end-testcase.xlsx", timeseries=True)
#     testcase.summary()
