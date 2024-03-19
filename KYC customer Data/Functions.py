import pandas as pd
import numpy as np
import re
import pandas as pd
import numpy as np
import re
class Shared_Contacts_DataCleaning:
    def __init__(self, df_data, usecols=None):
        self.df_data = df_data
        self.usecols = usecols


    def clean_data(self):
        cust_data = self.df_data
        email_data3 = cust_data.drop_duplicates(subset='customer_key', keep='first')
        email_data3['email_address'] = email_data3['email_address'].str.lower()
        email_data3['cell_phone_number'] = email_data3['cell_phone_number'].astype(str).str.rstrip('.0')

        def clean_email(email):
            if pd.isnull(email) or email.strip() == '':
                return ''
            if '@' not in email or '.' not in email:
                return ''
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                return ''
            return email

        email_data3['email_address'] = email_data3['email_address'].apply(clean_email)

        email_counts = email_data3['email_address'].value_counts()
        valid_emails = email_counts[(email_counts > 0) & (email_counts < 400)].index
        email_data3.loc[~email_data3['email_address'].isin(valid_emails), 'email_address'] = ''

        df_cleaned_emails = email_data3.copy()

        df_cleaned_emails['cell_phone_number'] = df_cleaned_emails['cell_phone_number'].replace({0: '', np.NAN: ''})
        df_cleaned_emails['cell_phone_number'] = df_cleaned_emails['cell_phone_number'].replace({np.nan: '', 'nan': ''})

        df_cleaned_emails['cell_phone_number'] = pd.to_numeric(df_cleaned_emails['cell_phone_number'], errors='coerce')
        mask = df_cleaned_emails['cell_phone_number'] < 9999999
        df_cleaned_emails.loc[mask, 'cell_phone_number'] = df_cleaned_emails.loc[mask, 'cell_phone_number'].apply(
            lambda x: '' if pd.isna(x) or round(x) < 9999999 else x)

        df_cleaned_emails['cell_phone_number'] = df_cleaned_emails['cell_phone_number'].fillna('')
        df_cleaned_emails['email_address'] = df_cleaned_emails['email_address'].fillna('')

        new_df2 = df_cleaned_emails.drop(df_cleaned_emails[
            (df_cleaned_emails['email_address'].eq('') | df_cleaned_emails['email_address'].isnull()) &
            (df_cleaned_emails['cell_phone_number'].eq('') | df_cleaned_emails['cell_phone_number'].isnull())].index)

        def format_phone_num(phone):
            return f'{phone}'
        new_df2['cell_phone_number'] = new_df2['cell_phone_number'].apply(format_phone_num)
        
        
        def clean_addresses(df):
            
            def validate_address(address):
                if pd.isnull(address) or address.strip() == '':
                    return ''
                pattern = r'^[a-zA-Z0-9._%+-]'
                if not re.match(pattern, address):
                    return ''
                return address
            df['physical_address'] = df['physical_address'].str.lower()
           
            
            df['physical_address'] = df['physical_address'].apply(validate_address)
           
            
            address_counts = df['physical_address'].value_counts()
            valid_addresses = address_counts[(address_counts > 0) & (address_counts < 400)].index
            df.loc[~df['physical_address'].isin(valid_addresses), 'physical_address'] = ''
            
        
            return df
        
        new_df2 = clean_addresses(new_df2)
        return new_df2

 
