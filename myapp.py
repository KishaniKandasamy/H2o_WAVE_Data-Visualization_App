from h2o_wave  import Q, main, app, ui,site,data
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import random

import os
import time
import logging


@app('/myapp')
async def serve(q: Q):
    if not q.client.initialized:
        initialize_app_for_new_client(q)

    if q.args.file_upload:
        await handle_uploaded_data(q)

    await q.page.save()


def initialize_app_for_new_client(q):
    

    q.page['header'] = ui.header_card(
        box='1 1 11 1',
        title='Wave Data Visualisation with UI Uploads and Downloads',
        subtitle='-Creditcard Fraud Detection',
    )

    render_upload_view(q)
    render_table_view(q)
    
    

    # Create a place to hold datasets where you are running wave
    q.client.data_path = './data'
    if not os.path.exists(q.client.data_path):
        os.mkdir(q.client.data_path)

    # Flag that this browser has been prepped
    q.client.initialized = True


def render_upload_view(q: Q):
    """Sets up the upload-dataset card"""
    q.page['upload'] = ui.form_card(
        box='1 2 3 -1',
        items=[
            ui.separator(label='Choose a Dataset'),
            ui.message_bar(
                type='info',
                text='This application requires a .csv file with CreditCard Fraud Detection data',
            ),
            ui.file_upload(name='file_upload', label='Upload Data', multiple=False, file_extensions=['csv']),
        ]
    )

def render_table_view(q: Q):
    """Sets up the view a file as ui.table card"""

    items = [ui.separator(label='View the Dataset')]

    if q.client.working_file_path is None:
        items.append(ui.message_bar(type='warning', text='Please upload a dataset!'))
    else:
        items.append(ui.text_xl(os.path.basename(q.client.working_file_path)))
        items.append(ui.message_bar(type='success', text='Files uploaded successfully !'))
        items.append(make_ui_table(file_path=q.client.working_file_path, n_rows=10, name='head_of_table'))
   

    q.page['table'] = ui.form_card(box='4 2 8 -1', items=items)

def make_ui_table(file_path: str, n_rows: int, name: str):
    """Creates a ui.table object from a csv file"""

    df = pd.read_csv(file_path)
    n_rows = min(n_rows, df.shape[0])

    table = ui.table(
        name=name,
        columns=[ui.table_column(name=str(x), label=str(x), sortable=True) for x in df.columns.values],
        rows=[ui.table_row(name=str(i), cells=[str(df[col].values[i]) for col in df.columns.values])
              for i in range(n_rows)]
    )
    return table

async def handle_uploaded_data(q: Q):
    """Saves a file uploaded by a user from the UI"""
    data_path = q.client.data_path

    # Download new dataset to data directory
    q.client.working_file_path = await q.site.download(url=q.args.file_upload[0], path=data_path)
    render_upload_view(q)

    file_path=q.client.working_file_path
    df = pd.read_csv(file_path)
   
    #view the table
    render_table_view(q)

    #make a bar stacked
    df_bar_stacked=  df.loc[:200,['AMT_INCOME_TOTAL','NAME_INCOME_TYPE','NAME_FAMILY_STATUS']]
    print(df_bar_stacked)
    v = q.page.add('df_bar_stacked', ui.plot_card(
    box='1 8 9 4',
    title='Make a stacked column plot',
    data=data(fields=df_bar_stacked.columns.tolist(),rows=df_bar_stacked.values.tolist()),
    plot=ui.plot(marks=[
        ui.mark(type='interval', 
        x='=NAME_INCOME_TYPE', y='=AMT_INCOME_TOTAL',
        color='=NAME_FAMILY_STATUS', stack='auto')
    ])
    ))

    #make a point sized plot
    df_point_sized =  df.loc[:200,['AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY']]
    v = q.page.add('point_plot_sized', ui.plot_card(
    box='1 12 5 2',
    title='Make a scatterplot with mark sizes mapped to a continuous variable (a "bubble plot")',
    data=data(fields=df_point_sized.columns.tolist(),rows=df_point_sized.values.tolist()),
    plot=ui.plot([
        ui.mark(type='point', 
        x='=AMT_INCOME_TOTAL', y='=AMT_CREDIT',size='=AMT_ANNUITY')
    ])
    ))

    #make a point plot
    df_point =  df.loc[:200,['DAYS_REGISTRATION','DAYS_ID_PUBLISH','NAME_EDUCATION_TYPE']]
    v = q.page.add('point_plot', ui.plot_card(
    box='6 12 5 2',
    title='Make a scatterplot..',
    data=data(fields=df_point.columns.tolist(),rows=df_point.values.tolist()),
    plot=ui.plot([
        ui.mark(type='point', 
        x='=DAYS_REGISTRATION', y='=DAYS_ID_PUBLISH',
        color='=NAME_EDUCATION_TYPE')
    ])
    ))

    #make a line plot
    df_line=  df.loc[:200,['SK_ID_CURR','NAME_INCOME_TYPE','AMT_INCOME_TOTAL']]
    v = q.page.add('df_line', ui.plot_card(
    box='1 14 5 2',
    title='Make a line plot',
    data=data(fields=df_line.columns.tolist(),rows=df_line.values.tolist()),
    plot=ui.plot(marks=[
        ui.mark(type='line', 
        x='=SK_ID_CURR', y='=AMT_INCOME_TOTAL', curve='smooth')
    ])
    ))

    #Make a line step plot
    df_line_step =  df.loc[:100,['SK_ID_CURR','NAME_INCOME_TYPE','AMT_INCOME_TOTAL']]
    v = q.page.add('df_heatmap', ui.plot_card(
    box='6 14 5 2',
    title='Make a line plot with a step curve',
    data=data(fields=df_line_step.columns.tolist(),rows=df_line_step.values.tolist()),
    plot=ui.plot([
        ui.mark(type='path', 
        x='=SK_ID_CURR', y='=AMT_INCOME_TOTAL', curve='step' ) 
    ])
    ))

    #Make an area plot
    df_area=  df.loc[:200,['AMT_INCOME_TOTAL','NAME_EDUCATION_TYPE','NAME_FAMILY_STATUS']]
    v = q.page.add('df_area', ui.plot_card(
    box='1 16 10 4',
    title='Make an area plot',
    data=data(fields=df_area.columns.tolist(),rows=df_area.values.tolist()),
    plot=ui.plot(marks=[
        ui.mark(type='area',
        x='=NAME_EDUCATION_TYPE', y='=AMT_INCOME_TOTAL',
        color='=NAME_FAMILY_STATUS')
    ])
    ))


    
    await q.page.save()

 