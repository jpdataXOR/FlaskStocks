from flask import Flask, render_template, request, session
import yfinance as yf
import pandas as pd
import re
import plotly.express as px
import pandas as pd
import json
from plotly.graph_objects import Figure
import plotly.offline as pyo
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ast
from datetime import datetime



app = Flask(__name__)
app.secret_key = 'flaskstocks-secret-key'

data_dic = {}
current_values=[]

@app.route("/", methods=['POST','GET'])
def index():
  global data_dic,current_values
  if request.method == 'POST' :
    if request.form.get('ASX') == 'ASX':
      data_dic,current_values = getStockData('ASX')
    elif request.form.get('NDQ') == 'NDQ':
      data_dic,current_values = getStockData('NDQ')
    else:
      data_dic={}
      current_values=[]
  else:
    print(f"get method ")
    
    #print(data_dic)
  current_table=makeVTableForCurrentValues(current_values)
  table_code=makeVTableForMatchedEntries(data_dic)
  #print(html_code)
  
  return render_template("index.html",
                         table=table_code,
                        current_table=current_table)



def makeTableForCurrentValues(current_values):
  data_string = ""
  
  # Add table headers
  data_string += "<tr><th>Date</th><th>Close</th><th>% Diff</th></tr>"
  
  for data in current_values:
      date = data['date']
      close = data['close']
      percentage_difference = data['percentage_difference']
      # Set cell color based on percentage_difference value
      cell_color = get_cell_color(percentage_difference)
      date_str = datetime.strftime(date, '%Y-%m-%d')
      data_string += f"<tr><td>{date_str}</td><td>{close}</td><td bgcolor='{cell_color}'>{percentage_difference}</td></tr>"
      
  html_code = f"""
    <table border="1">
        {data_string}
    </table>
    """
  
  return html_code
  
def makeVTableForCurrentValues(current_values):
  data_string = ""
  
  # Add table headers
  current_values = current_values[::-1]
  
  data_string += "<tr><th>Date</th>"
  for data in current_values:
      date_str = datetime.strftime(data['date'], '%Y-%m-%d')
      data_string += f"<th title='{data['close']}'>{date_str}</th>"
  data_string += "</tr>"
  
  # Add table rows
  data_string += "<tr><td>% Diff___________</td>"
  for data in current_values:
      percentage_difference = data['percentage_difference']
      # Set cell color based on percentage_difference value
      cell_color = get_cell_color(percentage_difference)
      percentage_difference_str = f"{percentage_difference:.2f}"
      data_string += f"<td bgcolor='{cell_color}' title='{data['close']}'>{percentage_difference_str}</td>"
  data_string += "</tr>"
      
  html_code = f"""
    <table border="1">
        {data_string}
    </table>
    """
  
  return html_code

def makeTableForMatchedEntries(data_dic):
  data_string = ""
  
  for find, data in data_dic.items():
        pattern = data[0]
        indices = data[1]
     
    
        cumulative_percentage = 0.0
        data_string += f"<tr><td>{find}</td><td>{pattern}</td><td>"
        for index in indices:
            date = index['date']
            close = index['close']
            percentage_difference = index['percentage_difference']
            cumulative_percentage += percentage_difference
            date_str = datetime.strftime(date, '%Y-%m-%d')
            data_string += f"{date_str} # {close} # {percentage_difference} <br>"
        data_string+="</td>"
        if cumulative_percentage < 0:
            data_string += f"<td bgcolor='red'>{cumulative_percentage}</td></tr>"
        else:
            data_string += f"<td bgcolor='green'>{cumulative_percentage}</td></tr>"
    
  html_code = f"""
    <table border="1">
        <tr>
            <th>Find</th>
            <th>Pattern</th>
            <th>Indices</th>
            <th>Cumulative Percentage</th>
        </tr>
        {data_string}
    </table>
    """
  
  return html_code

def makeVTableForMatchedEntries(data_dic):
  data_string = ""
  
  data_string += "<tr><th>Find_____</th><th>Pattern</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th><th style='white-space: nowrap;'>0000-00-00</th></tr>"
  for find, data in data_dic.items():
        pattern = data[0]
        indices = data[1]
        matched = data[2]
    
        cumulative_percentage = 0.0
        data_string += f"<tr><td>{datetime.strftime(indices[0]['date'],'%Y-%m-%d')}</td><td>{pattern}</td>"

        for i in range(8 - len(matched)):
                data_string += "<td></td>"
          
        for index in reversed(matched):
            date = index['date']
            close = index['close']
            percentage_difference = index['percentage_difference']
            cumulative_percentage += percentage_difference
            date_str = datetime.strftime(date, '%Y-%m-%d')
            cell_color = get_cell_color(percentage_difference)
            percentage_difference_str = f"{percentage_difference:.2f}"
            
            # Fill in blank <td> elements
            
            
            # Add data for matching indices
            data_string += f"<td bgcolor='{cell_color}' title='{close},{date_str}'>{percentage_difference_str}</td>"
        
        data_string+="<td>.</td>"
        for index in indices:
            date = index['date']
            close = index['close']
            percentage_difference = index['percentage_difference']
            cumulative_percentage += percentage_difference
            date_str = datetime.strftime(date, '%Y-%m-%d')
            cell_color = get_cell_color(percentage_difference)
            percentage_difference_str = f"{percentage_difference:.2f}"
            data_string += f"<td bgcolor='{cell_color}' title='{close},{date_str}'>{percentage_difference_str}</td>"
        if cumulative_percentage < 0:
            data_string += f"<td bgcolor='red'>{cumulative_percentage}</td></tr>"
        else:
            data_string += f"<td bgcolor='green'>{cumulative_percentage}</td></tr>"
    
  html_code = f"""
    <table border="1">
        {data_string}
    </table>
    """
  
  return html_code



def get_cell_color(value):
  if value < -2:
    return "#800000"  # dark red
  elif value < -1:
    return "#FF0000"  # red
  elif value < -0.5:
    return "#FFA07A"  # mild red
  elif value < 0:
    return "#FF4500"  # light red
  elif value == 0:
    return "white"
  elif value < 0.5:
    return "#90EE90"  # light green
  elif value < 1:
    return "#006400"  # mild green
  elif value < 2:
    return "#008000"  # green
  else:
    return "#006400"  # dark green



@app.route("/plot", methods=['GET'])
def plot():
  # Obtain data from query parameters
  x1 = request.args.get('x1')
  y1 = request.args.get('y1')
  x2 = request.args.get('x2')
  y2 = request.args.get('y2')

  x1 = ast.literal_eval(x1)
  y1 = ast.literal_eval(y1)
  x2 = ast.literal_eval(x2)
  y2 = ast.literal_eval(y2)


  display_result = request.args.get('display_result')
  # Create figure with secondary y-axis
  fig = make_subplots(specs=[[{"secondary_y": True}]])
  # Add traces
  fig.add_trace(
    go.Scatter(x=x1, y=y1, name="Current Data"),
    secondary_y=False,
  )
  fig.add_trace(
    go.Scatter(x=x2, y=y2, name="Extrapolate data"),
    secondary_y=True,
  )
  # Add figure title
  fig.update_layout(
    title_text="Extrapolations"
  )
  # Set x-axis title
  fig.update_xaxes(title_text="Dates ")
  # Set y-axes titles
  fig.update_yaxes(title_text="<b>Current</b>", secondary_y=False)
  fig.update_yaxes(title_text="<b>Past</b>", secondary_y=True)
  # Render plot
  plot = pyo.plot(fig, output_type='div')
  # Render template with plot and display_result
  return render_template("index.html", plot=plot, display_result=display_result)




def getStockData(arg_method='ASX'):
  axjo = yf.Ticker("^AXJO")
  arrayData = axjo.history(period="max")
  #for col in arrayData.columns:
  # print(col)
  #open , high ,low close
  #name = date

  resultString = ''
  # Print Last 2 days
  print(arrayData.iloc[-1].name)
  print(arrayData.iloc[-2].name)
  #Last Day Close
  print(str(arrayData.iloc[-1]['Close']))
  # Oldest to Latest
  for i in range(1, len(arrayData)):
    difference = (
      ((arrayData.iloc[i]['Close'] - arrayData.iloc[i - 1]['Close']) /
       arrayData.iloc[i - 1]['Close']) * 100.00)
    #print(str(arrayData.iloc[i].name).split()[0], difference)
    if difference >= 0:
      resultString += 'U'
    else:
      resultString += 'D'

  #print(resultString[0:10])
  #Reverse dataFame
  arrayData = arrayData.iloc[::-1]
  #reverse the string
  resultString = resultString[::-1]
  #Print the Latest Result Today,yesterday,daybefore etc
  print(resultString[0:10])

  index_dict = {}
  for iteration in range(8, 5, -1):
    #print(iteration)
    stringToMatch = (resultString[0:iteration])
    indices_object = re.finditer(pattern=stringToMatch,
                                 string=resultString[0:])
    indices = [index.start() for index in indices_object]
    #print(stringToMatch)
    #print(len(indices))
    #print(indices)
    if len(indices) > 2:
      # Simplest pick the second only as first is anyway the current /todays =>index = indices[1]
      #print(index)
      for matchedIndex in indices[1:]:
        if matchedIndex not in index_dict:
          index_dict[matchedIndex] = len(stringToMatch)
    #print(arrayData.iloc[index].name, arrayData.iloc[index]
    #['Close'])
  # print(arrayData.iloc[index + 1].name, arrayData.iloc[index + 1]['Close'])

  #print(index_dict)
  for key, value in index_dict.items():
      indices,matched=printDifferenceData(arrayData, key, value, 3)
      index_dict[key] = (value, indices,matched)

  # Get last 5 values 
  currentValues=[]
  for count in range(0, 8):
    this_value = arrayData.iloc[count+1]['Close']
    future_value= arrayData.iloc[count]['Close']
    percentage_difference = (future_value - this_value) / this_value * 100
    currentValues.append({
        'date': arrayData.iloc[count].name,
        'close': arrayData.iloc[count]['Close'],
        'percentage_difference': percentage_difference
    })
    
  return index_dict,currentValues





def printDifferenceData(arg_Array, index, matchedLength, forwardLength):

  # print("{}  and {}".format(index, matchedLength))
  """
  Example
  2001-06-05 00:00:00+10:00 -- 3422.199951171875
  2001-06-04 00:00:00+10:00 -- 3426.699951171875
  2001-06-01 00:00:00+10:00 -- 3391.5
  2001-05-31 00:00:00+10:00 -- 3379.10009765625
  2001-05-30 00:00:00+10:00 -- 3399.800048828125
  2001-05-29 00:00:00+10:00 -- 3411.10009765625
  2001-05-28 00:00:00+10:00 -- 3420.10009765625
  2001-05-25 00:00:00+10:00 -- 3426.10009765625
  """
  """
  #This prints current 
  for count in range(0, matchedLength):
    this_value = arg_Array.iloc[count+1]['Close']
    future_value= arg_Array.iloc[count]['Close']
    percentage_difference = (future_value - this_value) / this_value * 100
    print(
      str(arg_Array.iloc[count].name) + " -- " +
      str(arg_Array.iloc[count]['Close'])+" -- "+str(percentage_difference))

  print()  
     
  # This prints what was matched
  for count in range(index, index + matchedLength):
    this_value = arg_Array.iloc[count+1]['Close']
    future_value= arg_Array.iloc[count]['Close']
    percentage_difference = (future_value - this_value) / this_value * 100
    print(
      str(arg_Array.iloc[count].name) + " -- " +
      str(arg_Array.iloc[count]['Close'])+" -- "+str(percentage_difference))

  print()

  
  """
  #what matched 
  matched=[]
  for count in range(index, index + matchedLength):
    this_value = arg_Array.iloc[count+1]['Close']
    future_value= arg_Array.iloc[count]['Close']
    percentage_difference = (future_value - this_value) / this_value * 100
    """
    print(
      str(arg_Array.iloc[count].name) + " -- " +
      str(arg_Array.iloc[count]['Close'])+" -- "+str(percentage_difference))
    """
    matched.append({
        'date': arg_Array.iloc[count].name,
        'close': arg_Array.iloc[count]['Close'],
        'percentage_difference': percentage_difference
    })


  
  indices = []
  for count in range(index, index - forwardLength, -1):

    future_value = arg_Array.iloc[count - 1]['Close']
    this_value = arg_Array.iloc[count]['Close']
    percentage_difference = (future_value - this_value) / this_value * 100
    """
    print(
      str(arg_Array.iloc[count].name) + " -- " +
      str(arg_Array.iloc[count]['Close']) + " -- " +
      str(percentage_difference))
    """
    indices.append({
        'date': arg_Array.iloc[count].name,
        'close': arg_Array.iloc[count]['Close'],
        'percentage_difference': percentage_difference
    })
  return indices,matched


###########################################




app.run(host='0.0.0.0', port=81)
########################################
