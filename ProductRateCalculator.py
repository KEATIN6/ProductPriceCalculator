#!/usr/bin/env python
# coding: utf-8

# In[32]:


import numpy_financial as npf
import pandas as pd

class ProductRateCalculator():
    
    def __init__(self, present_value, product_name=None):
        rates = self.calculate_all_rates(present_value)
        self.rate_df = self.prepare_df_rates(rates)
        if product_name :
            self.product_name = product_name
            self.rename_results(product_name)     
        else:
            self.product_name = 0
        
    def calculate_maas_rate(self, present_value):
        term = 24
        maas_rate = round(present_value/term, 2)
        return maas_rate

    def calculate_finance_rate(self, present_value, term):
        interest_rate = .125
        finance_rate = round(npf.pmt(interest_rate/12, term, present_value, 0)*-1, 2)
        return finance_rate

    def calculate_all_rates(self, present_value):
        if present_value-450 <= 0 :
            contract_rate = 0
        else:
            contract_rate = present_value-450
        maas_rate = self.calculate_maas_rate(present_value)
        finance_24M_rate = self.calculate_finance_rate(present_value, 24)
        finance_36M_rate = self.calculate_finance_rate(present_value, 36)
        rates = {
            "Retail":present_value,
            "Contract":contract_rate,
            "MaaS":maas_rate,
            "24MFinance":finance_24M_rate,
            "36MFinance":finance_36M_rate
        }
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
            self.rate_df.at[self.product_name, finance_term] = clean_finance_rate(
                self.rate_df[finance_term][self.product_name])
    
    def rename_results(self, new_name):
        self.rate_df.rename(index={0: new_name}, inplace=True)

    def print_results(self):
        if self.product_name and self.product_name != 0 :
            print('Product Name: {}'.format(self.product_name))
        print(
            """Retail Price: ${}\n"""
            """Contract Price: ${}\n"""
            """MaaS Price: ${}\n"""
            """24M Finance Price: ${}\n"""
            """36M Finance Price: ${}"""
            .format(self.rate_df['Retail'][0], self.rate_df['Contract'][0], self.rate_df['MaaS'][0], 
                    self.rate_df['24MFinance'][0], self.rate_df['36MFinance'][0])
        )


# In[39]:


results = ProductRateCalculator(399, 'Apple iPhone SE (2020) 64GB')
results.rate_df


# In[41]:


results.clean_finance_rates()
results.print_results()


# In[ ]:





# In[ ]:




