# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 11:42:04 2022

@author: pizzacoin
"""
# %% Import the used libraries

import wx
import pandas as pd
import numpy_financial as npf

from ObjectListView import ObjectListView, ColumnDefn 

# %% Set constants for interest and subsidy

CONTRACT_SUBSIDY = 450
FINANCE_RATE = .125

# %%

class ProductRateCalculator():
    
    def __init__(self, present_value, product_name=None):
        self.present_value = int(present_value)
        rates = self.calculate_all_rates(self.present_value)
        self.rate_df = self.prepare_df_rates(rates)
        if product_name :
            self.product_name = product_name
            self.rename_results(product_name)     
        else:
            self.product_name = "Undefined Product"
        
    def calculate_maas_rate(self, present_value):
        term = 24
        maas_rate = round(present_value / term, 2)
        return maas_rate

    def calculate_finance_rate(self, present_value, term):
        finance_rate = round(-1 * npf.pmt(
            FINANCE_RATE / 12, term, present_value, 0), 2)
        return finance_rate

    def calculate_all_rates(self, present_value):
        if present_value <= CONTRACT_SUBSIDY:
            contract_rate = 0
        else:
            contract_rate = (present_value - CONTRACT_SUBSIDY)
        maas_rate = self.calculate_maas_rate(present_value)
        finance_24M_rate = self.calculate_finance_rate(present_value, 24)
        finance_36M_rate = self.calculate_finance_rate(present_value, 36)
        rates = {"Retail": present_value,
                 "Contract": contract_rate,
                 "MaaS": maas_rate,
                 "24MFinance": finance_24M_rate,
                 "36MFinance": finance_36M_rate}
        return rates

    def prepare_df_rates(self, rates):
        df = pd.DataFrame()
        df['Retail'] = [rates['Retail']]
        df['Contract'] = [rates['Contract']]
        df['MaaS'] = [rates['MaaS']]
        df['24MFinance'] = [rates['24MFinance']]
        df['36MFinance'] = [rates['36MFinance']]
        return df
    
    def clean_finance_rates(self):
        
        finance_terms = ['24MFinance','36MFinance']
        
        def clean_finance_rate(current_rate):
            decimal_amount = current_rate % 1
            if (.99-decimal_amount) > (decimal_amount-.49) :
                if decimal_amount < .15 :
                    cleaned_rate = current_rate-decimal_amount-.01
                else:
                    cleaned_rate = current_rate-decimal_amount+.49
            else :
                cleaned_rate = current_rate-decimal_amount+.99
            return cleaned_rate
        
        for finance_term in finance_terms:
            self.rate_df.at[self.product_name, finance_term] = \
                clean_finance_rate(
                    self.rate_df[finance_term][self.product_name])
    
    def rename_results(self, new_name):
        self.rate_df.rename(index={0: new_name}, inplace=True)

    def print_results(self):
        if self.product_name and self.product_name != 0 :
            print('Product Name: {}'.format(self.product_name))
        print("""------------------------------------------\n"""
            """     Retail Price: ${:9,.2f}\n"""
            """   Contract Price: ${:9,.2f}\n"""
            """       MaaS Price: ${:9,.2f}\n"""
            """24M Finance Price: ${:9,.2f}\n"""
            """36M Finance Price: ${:9,.2f}\n"""
            """------------------------------------------"""
            .format(self.rate_df['Retail'][0], self.rate_df['Contract'][0], 
                    self.rate_df['MaaS'][0], self.rate_df['24MFinance'][0], 
                    self.rate_df['36MFinance'][0]))
        
# %% Class to house the pricing dataframe
        
class ProductRates:
    def __init__(self, product_rate_list=None):
        
        self.product_rate_df = pd.DataFrame()
        
        if product_rate_list and type(product_rate_list) == list:
            for product_price_tuple in product_rate_list:
                self.add_product(product_price_tuple)

    def load_dataframe(self, df_to_load):
        self.product_rate_df = pd.concat([self.product_rate_df, df_to_load])
            
    def add_product(self, product_price_tuple):
        retail_rate, product_name= product_price_tuple
        prc = ProductRateCalculator(retail_rate, product_name)
        self.product_rate_df = pd.concat([self.product_rate_df, prc.rate_df])
        
        
# %%

class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.rate_results = []
        
        main_vert_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(self, label="Product Rate Calculator")
        
        
        main_vert_sizer.Add(title)
        
        self.price_olv = ObjectListView(
            self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.price_olv.SetEmptyListMsg("Please add a record")
        
        main_vert_sizer.Add(self.price_olv, 1, wx.EXPAND|wx.ALL)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn01 = wx.Button(self, label="Add Record", size=(100,-1))
        self.btn01.Bind(wx.EVT_BUTTON, self.add_record)
        self.btn02 = wx.Button(self, label="Remove Record", size=(100,-1))
        self.btn03 = wx.Button(self, label="Export Excel", size=(100,-1))
        
        button_sizer.Add(self.btn01, 0, wx.CENTER, 5)
        button_sizer.Add(self.btn02, 0, wx.CENTER, 5)
        button_sizer.Add(self.btn03, 0, wx.CENTER, 5)
                
        main_vert_sizer.Add(button_sizer, 0, wx.CENTER, 0)
        
        self.SetSizerAndFit(main_vert_sizer)
        self.update_olv()
        
        
    def add_record(self, event):
        with RecordDialog() as dlg:
            dlg.ShowModal()
    
        
    def update_olv(self):
        self.price_olv.SetColumns([
            ColumnDefn('Product Name', 'left', 225, 'product_name'),
            ColumnDefn('Retail Rate', 'right', 100, 'retail'),
            ColumnDefn('Contract Rate', 'right', 100, 'contract'),
            ColumnDefn('MDaaS Rate', 'right', 100, 'mdaas'),
            ColumnDefn('24M Finance', 'right', 100, 'finance_24m'),
            ColumnDefn('36M Finance', 'right', 100, 'finance_36m')])
        self.price_olv.SetObjects(self.rate_results)


# %%

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Product Rate Calculator", 
                         size=(800,400))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_01 = MainPanel(self)
        self.sizer.Add(self.panel_01, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        
# %%

class RecordDialog(wx.Dialog):
    def __init__(self, row=None, parent=None, 
                 title="Add", addRecord=True):
        super().__init__(None, title=f"{title} New Product Rate Record")
        self.addRecord = addRecord
        self.selected_row = row
        self.parent = parent
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        size = (100, -1)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        
        product_name_lbl = wx.StaticText(self, label="Product Name", size=size)
        product_name_ctrl = wx.TextCtrl(self, value="", size=(200,-1))
        
        main_sizer.Add(self.row_builder([product_name_lbl, product_name_ctrl]))
        
        product_rate_lbl = wx.StaticText(self, label="Retail", size=size)
        product_rate_ctrl = wx.TextCtrl(self, value="", size=(200,-1))
        
        main_sizer.Add(self.row_builder([product_rate_lbl, product_rate_ctrl]))
        
        self.SetSizerAndFit(main_sizer)
        

    def row_builder(self, widgets):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label, text = widgets
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(text, 0, wx.ALL, 5)
        return sizer

        
        
# %%

if __name__ == "__main__":
    
    results = [(1399, 'Apple iPhone SE (2020) 64GB'),
               ('799', 'Samsung Galaxy S22')]
    
    z = ProductRates(results)
    print(z.product_rate_df)
    
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
    del app
    
        
# %%
