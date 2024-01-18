import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import math


from streamlit_login_auth_ui.widgets import __login__ 
def Login():
    __login__obj = __login__(auth_token = "pk_prod_RKF21ZJ374M8NQN9HC3BVW37PK4G", 
                        company_name = "TST",
                        width = 200, height = 250, 
                        logout_button_name = 'Logout', hide_menu_bool = False, 
                        hide_footer_bool = False, 
                        lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')
    LOGGED_IN = __login__obj.build_login_ui()
    email = __login__obj.get_email()
    if email=="manager@tn-smart-tech.com":
        return True
    else:
        return False
def twoConsecutiveDates(day1: str, day2: str):
    day1 = day1.split("-")
    day2 = day2.split("-")
    if day1[0] == day2[0] and day1[1] == day2[1]:
        if abs(int(day1[2])-int(day2[2])) == 1:
            return True
    #add more cases (end of month, end of year)
    return False
if Login():
    if "mmsi" not in st.session_state:
        st.session_state.mmsi = None
    if "date" not in st.session_state:
        st.session_state.date = None
    if "mmsiIndex" not in st.session_state:
        st.session_state.mmsiIndex = None
    if "dateIndex" not in st.session_state:
        st.session_state.dateIndex = None
    if "data" not in st.session_state:
        st.session_state.data = []



            

    df = pd.read_csv('aisQuery.csv', sep=',',header =0, index_col=False)
    Navigation= df[["mmsi", "dateAis", "timeAis", "lon", "lat"]]

    #clean data
    thresh_min= 0.01
    thresh_max= 0.99
    LAT_min= Navigation['lat'].quantile(thresh_min)
    LAT_max= Navigation['lat'].quantile(thresh_max)
    LON_min= Navigation['lon'].quantile(thresh_min)
    LON_max= Navigation['lon'].quantile(thresh_max)
    Navigation= Navigation[(Navigation['lat']<LAT_max) & (Navigation['lat']>LAT_min)]
    Navigation= Navigation[(Navigation['lon']<LON_max) & (Navigation['lon']>LON_min)]


    #select the mmsi from the list
    #mmsi = st.sidebar.selectbox("Select a mmsi", Navigation["mmsi"].unique())
    if st.session_state.mmsi is None:
        #take the first mmsi from the list
        mmsi = Navigation["mmsi"].unique()[0]
        st.session_state.mmsi = mmsi
        st.session_state.mmsiIndex = 0
    else:
        mmsiIndex = st.session_state.mmsiIndex
        mmsi= Navigation["mmsi"].unique()[mmsiIndex]
        st.session_state.mmsi = mmsi
        if mmsiIndex >= len(Navigation["mmsi"].unique())-1:
            st.stop()

    #create a new dataframe with the selected mmsi
    selected_mmsi = Navigation[Navigation["mmsi"] == mmsi]
    #sort by date and time
    selected_mmsi= selected_mmsi.sort_values(by=['dateAis', 'timeAis'])





    dates=list(selected_mmsi["dateAis"].unique())
    dates.sort()
    #if two dates are consequtive and the difference between them is less than 3 hour they are considered the same date
    prev = None
    for nav in selected_mmsi.iterrows():
        if prev is None:
            prev = nav[1]
        else:
            if twoConsecutiveDates(prev["dateAis"], nav[1]["dateAis"]):
                timeDiff = pd.to_datetime(nav[1]["timeAis"], format='%H:%M:%S') - pd.to_datetime(prev["timeAis"], format='%H:%M:%S')
                if timeDiff< pd.Timedelta(hours=3):
                    #dates.remove(nav[1]["dateAis"])
                    #dates.remove(prev["dateAis"])
                    dates.append(prev["dateAis"]+"/"+nav[1]["dateAis"])
                    dates.sort()
            prev = nav[1]





        


    #select between all and specific date from the list
    #date = st.sidebar.selectbox("Select a date", ["all"] + dates)

    if st.session_state.date is None:
        #take the first date from the list
        st.session_state.date = dates[0]
        st.session_state.dateIndex = 0
    else:
        dateIndex = st.session_state.dateIndex
        if dateIndex >= len(dates)-1:
            st.session_state.dateIndex = 0
            st.session_state.date = None
            st.session_state.mmsiIndex += 1
            st.rerun()
            st.stop()
        else:
            st.session_state.date= dates[dateIndex]

    date = st.session_state.date
    dateIndex = st.session_state.dateIndex


    isMoreThanOneDate = False
    if "/" in date:
        isMoreThanOneDate = True
        date = date.split("/")
    if not isMoreThanOneDate:
        to_plot = selected_mmsi if date == "all" else selected_mmsi[selected_mmsi["dateAis"] == date]
    else:
        to_plot1 = selected_mmsi[selected_mmsi["dateAis"] == date[0]]
        to_plot2= selected_mmsi[selected_mmsi["dateAis"] == date[1]]
        to_plot = to_plot1.merge(to_plot2, how='outer')
        


    st.map(to_plot)

    def next(dateIndex):
        dateIndex += 1
        st.session_state.dateIndex = dateIndex
        # if dateIndex >= len(dates)-1:
        #     st.session_state.dateIndex = 0
        #     st.session_state.date = None
        #st.rerun()
        #st.stop()
    st.write("Date: ", date)
    st.write("MMSI: ", mmsi)
    # st.button("Next", on_click=next, args=(dateIndex,))
    def grade(mmsi,date,dateIndex,grade):
        st.session_state.data.append([mmsi,date,grade])
        df=pd.DataFrame(st.session_state.data,columns=['mmsi','date','grade'])
        df.to_csv('grades.csv',index=False)
        next(dateIndex)

    grades=["very safe","safe","neutral","unsafe","very unsafe"]
    b1,b2,b3,b4,b5=st.columns(5)
    with b1:
        st.button(grades[0], on_click=grade, args=(mmsi,date,dateIndex,1))
    with b2:
        st.button(grades[1], on_click=grade, args=(mmsi,date,dateIndex,2))
    with b3:
        st.button(grades[2], on_click=grade, args=(mmsi,date,dateIndex,3))
    with b4:
        st.button(grades[3], on_click=grade, args=(mmsi,date,dateIndex,4))
    with b5:
        st.button(grades[4], on_click=grade, args=(mmsi,date,dateIndex,5))





        



        



