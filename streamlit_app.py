import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title='The getaround dashboard',
    page_icon=' 🚗',
    layout='wide'
)


### Loading Dataset in cache
@st.cache_data
def load_data():
    data_price = pd.read_csv('./src/get_around_pricing_project.csv', index_col=[0])
    data_delay = pd.read_excel('./src/get_around_delay_analysis.xlsx')
    return data_price, data_delay

data_price, data_delay = load_data()

### Headers
st.image('./src/getaround_logo.png', width=200)
st.title('The getaround dashboard.')
st.markdown('---')

st.subheader('How to ***reduce the friction*** with a ***feature*** implementing a ***minimum delay*** between rentals while ***limiting revenue loss***? 🚗')
st.markdown('---')

##############################################################################
### defining functions. To include in a tool script later and import it to optimize computation.
def convert_m_to_h(data, col_name: str):
    ''' Will convert a minute column in hours '''
    new_col = f'{col_name}_converted_in_hours'
    data[new_col] = data[col_name]/60

def friction(threshold):
    '''Will calculate the number of problematic cases (friction) remaining among late drivers after defining threshold '''

    friction = threshold < data_late['delay_at_checkout_in_minutes_converted_in_hours']
    nb_prob = friction.sum()
    late_percentage = nb_prob/len(data_late)
    # print(f'There was {late_percentage*100:.2f}% of friction ({nb_prob} problematic cases) corrected with a {threshold}h threshold.')
    return nb_prob, late_percentage

def trim_thres(i):
    '''Will trim the entire dataset of drivers based on defined threshold and return potential loss in absolute and percentage value as a tuple '''

    delta_tot = data_delay['time_delta_with_previous_rental_in_minutes_converted_in_hours'] >= i
    delta_na_tot = data_delay['time_delta_with_previous_rental_in_minutes_converted_in_hours'].isna()
    data_delay_thres = data_delay[delta_tot | delta_na_tot]
    pot_loss_tot = len(data_delay) - len(data_delay_thres)
    pot_loss_per_tot = pot_loss_tot / len(data_delay)
    return pot_loss_tot, pot_loss_per_tot
    # print(f'The potential loss with a threshold impacts {pot_loss_per_tot * 100:.2f} % ({pot_loss_tot} rentals) of all the recorded rentals (late or not).')

def trim_thres_late(i):
    '''Will trim the dataset of late drivers based on defined threshold and return potential loss in absolute and percentage value as a tuple '''

    delta_thres = data_late['time_delta_with_previous_rental_in_minutes_converted_in_hours'] >= i
    delta_na = data_late['time_delta_with_previous_rental_in_minutes_converted_in_hours'].isna()
    data_delta_thres = data_late[delta_thres | delta_na]
    pot_loss = len(data_late) - len(data_delta_thres)
    pot_loss_per = pot_loss / len(data_late)
    # print(f'The potential loss with a threshold impacts {pot_loss_per * 100:.2f} % ({pot_loss} rentals) of the recorded rentals that were late.')
    return pot_loss, pot_loss_per

def revenue_loss(pot_loss_per):
    '''Will estimate the potential revenue loss per day based on result from the function trim_thres_late() and return loss and adjusted loss per day (relative to the entire dataset, 
    late or not, corrected for the % of late drivers) as a tuple'''

    late_per = len(data_late) / len(data_delay_trim)
    price_day = data_price['rental_price_per_day'].sum()
    price_day_late = price_day*late_per
    price_day_late_adjust = price_day_late - (price_day_late * pot_loss_per)
    price_day_adjust = price_day_late_adjust + (price_day*(1-late_per))
    # print(f'The total revenue per day (assumed) with the feature activated would be of {price_day_adjust:,.2f}$, which corresponds to an absolute loss of {price_day-price_day_adjust:,.2f}$ ({(price_day-price_day_adjust)/price_day*100:.2f} %) per day')
    return price_day, price_day_adjust, late_per

##############################################################################

#### Adding columns in hours for delay and delta
convert_m_to_h(data_delay, 'delay_at_checkout_in_minutes')
convert_m_to_h(data_delay, 'time_delta_with_previous_rental_in_minutes')

### Remove NA from delay
twelvecond = data_delay['delay_at_checkout_in_minutes_converted_in_hours'].between(-12, 12)
data_delay_trim = data_delay[twelvecond]

### Isolating data from late drivers only
delay_late = data_delay_trim['delay_at_checkout_in_minutes'] > 0
data_late = data_delay_trim[delay_late]

########################### Some basics data to understand
st.header('Here are some basic data about late drivers')
st.markdown('')

col1, col2 = st.columns(2)

with col1:
    ### Late drivers
    st.subheader('57 % of drivers are late ⌚')
    st.markdown('***Negative values represent late drivers***')

    hist_delay = px.histogram(data_delay_trim, y='delay_at_checkout_in_minutes_converted_in_hours',
                             labels={'delay_at_checkout_in_minutes_converted_in_hours': 'Delay at checkout in hours'},
                             color_discrete_sequence=['lightblue'])
    hist_delay.add_hline(y=0, line_color='purple')
    st.plotly_chart(hist_delay)

with col2:
    ### Checkin method among late drivers
    st.subheader('Most drivers are late in a 2h window ⌚')
    st.markdown('***Regardless of check-in method***')

    hist_late = px.histogram(data_late, 'delay_at_checkout_in_minutes_converted_in_hours', color='checkin_type',
                             color_discrete_map={'mobile': 'lightblue', 'connect': 'purple'},
                             labels={'delay_at_checkout_in_minutes_converted_in_hours': 'Delay at checkout in hours'})
    st.plotly_chart(hist_late)

st.markdown('---')

################################### Threshold

st.header('Threshold: how long should the minimum delay be?')

#### Calculating friction for a variety of threshold (from 0 to 12h with a step of 30min)
# 0.5 h is 30 min
fric_dic = {}
for i in np.arange(0, 12.5, 0.5):
    _, late_percentage = friction(i)
    fric_dic[i] = late_percentage*100

data_late_mean = data_late['delay_at_checkout_in_minutes_converted_in_hours'].mean()

threshold = st.slider('Select your threshold (in hours).', 0.0, 12.0, step=0.5, format='')

thres = px.line(x=list(fric_dic.keys()), y=list(fric_dic.values()), title='Friction (% of problematic cases) among late drivers against hours.', labels={'x': 'Threshold in hours', 'y': 'Percentage of friction'})
thres.add_vline(x=data_late_mean, line_color='purple')
thres.add_vline(x=threshold, line_color='red')
thres.add_annotation(x=data_late_mean-0.1, y=max(fric_dic.values()) , text='Mean delay', textangle=-90, showarrow=False)
thres.add_annotation(x=threshold+0.1, y=max(fric_dic.values()) , text=f'Threshold of {threshold}h', textangle=-90, showarrow=False)
thres.update_xaxes(dtick=1)
st.plotly_chart(thres, use_container_width=True)
st.markdown(f'There is still a <span style="color: red;"> **{fric_dic[threshold]:.2f}%** </span> of friction with a threshold of <span style="color: red;"> **{threshold}h** </span>.', unsafe_allow_html=True)
st.markdown('Whereas the threshold of 1.5h seems to efficiently reduce the amount of friction among delayed end-of-rental, the window could be considered to up to ~3h, above which the feature efficiency would be less significant.')


################################## Revenue loss
st.header('Which share of our owner’s revenue would potentially be affected by the feature?')

# data_delta_thres = the remaining rentals if the feature was enabled on all cars (mobile + connect)
delta_thres = data_late['time_delta_with_previous_rental_in_minutes_converted_in_hours'] >= 1.5
delta_na = data_late['time_delta_with_previous_rental_in_minutes_converted_in_hours'].isna()
data_delta_thres = data_late[delta_thres | delta_na]

loss, impact = st.columns(2, gap='large')

with loss:
    ## Amount of revenue loss
    pot_loss, pot_loss_per = trim_thres_late(threshold)
    price_day, price_day_adjust, late_per = revenue_loss(pot_loss_per)
    revenue_loss_percentage = (price_day - price_day_adjust) / price_day * 100
    remaining_percentage = 100 - revenue_loss_percentage
    
    # pie chart
    revenue_loss_data = {'Category': ['Revenue Loss', 'Remaining Revenue'], 'Percentage': [revenue_loss_percentage, remaining_percentage]}
    pie_revenue_loss = px.pie(revenue_loss_data, names='Category', values='Percentage', title='Revenue Loss', color_discrete_sequence=['lightblue', 'purple'])
    st.plotly_chart(pie_revenue_loss)

    st.markdown(f'The total revenue loss with the feature activated with a threshold of <span style="color: red;"> **{threshold}h** </span> would be of <span style="color: red;"> **{price_day_adjust:,.2f} \$** </span> which corresponds to an absolute loss of <span style="color: red;"> **{price_day-price_day_adjust:,.2f} $** </span> (<span style="color: red;"> **{revenue_loss_percentage:.2f} %** </span>) per day (presumably)', unsafe_allow_html=True)



with impact:
    ## Nb of rentals impacted (when adjusted for the complete dataset, late or not)
    pot_loss_tot, pot_loss_per_tot = trim_thres(threshold)
    impact_percentage = pot_loss_per_tot * 100
    remaining_impact_percentage = 100-impact_percentage

    # pie chart
    rental_loss_data = {'Category': ['Rentals Loss', 'Remaining Rentals'], 'Percentage': [impact_percentage, remaining_impact_percentage]}
    pie_rental_loss = px.pie(rental_loss_data, names='Category', values='Percentage', title='Rental Loss', color_discrete_sequence=['lightblue', 'purple'])
    st.plotly_chart(pie_rental_loss)

    st.markdown(f'The potential loss with a threshold of <span style="color: red;"> **{threshold}h** </span> impacts <span style="color: red;"> **{impact_percentage:.2f}** % </span> (<span style="color: red;">**{pot_loss_tot}** </span> rentals) of all the recorded rentals (late or not).', unsafe_allow_html=True)



################################### Scope

st.header('Scope: should we enable the feature for all cars?, only Connect cars?')
st.markdown('Given the small proportion of cars rented through the use of Connect in comparison of mobile, it is not recommended to activate the feature only on cars with the connect feature. See the histogram above showing the count of mobile vs connect among late users.')
st.markdown('---')