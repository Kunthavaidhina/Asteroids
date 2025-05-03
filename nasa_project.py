import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector as db



connection=db.connect(host='localhost',
                      user='root',
                      password='Mithran@21',
                      database='training')
cursur=connection.cursor()


st.set_page_config(page_title="NASA NEO Tracking", page_icon=":rocket:", layout="wide")
st.markdown("""### 🚀 NASA Near-Earth Object (NEO) Tracking & Insights using Public API""")

Filter=st.write("Filter creteria:")
left,middle,right=st.columns(3,vertical_alignment="bottom")
with left:
    astronomical=st.slider("Select astronomical range", min_value=0.000937, max_value=0.493661,value=(0.000937, 0.493661))
    miss_distance_lunar=st.slider("Select lunar distance range", min_value=0.364618, max_value=192.034000, value=(0.364618, 192.034000))
    relative_velocity_kmph=st.slider("Select relative velocity range", min_value=9522.503906, max_value=126807.304688, value=(9522.503906, 126807.304688))
with middle:
    estimated_diameter_min=st.slider("Select estimated diameter MIN range", min_value=0.003362, max_value=4.597850 , value=(0.0, 5.0))
    estimated_diameter_max=st.slider("Select estimated diameter MAX range", min_value=0.007517, max_value=10.28, value=(10.28, 0.0))
    is_potentially_hazardous_asteroid=st.selectbox("Select hazardous state", options=["0","1"])
with right:
    start_date=st.date_input("Select start date", value=datetime(2024, 1, 1))
    end_date=st.date_input("Select end date", value=datetime(2024, 1, 8))
dat=('''select asteroids.id, 
    asteroids.name, 
    asteroids.is_potentially_hazardous_asteroid, 
    asteroids.estimated_diameter_min, 
    asteroids.estimated_diameter_max, 
    asteroids.absolute_magnitude_h,
    close_approach.close_approach_date, 
    close_approach.miss_distance_km, 
    close_approach.miss_distance_lunar, 
    close_approach.astronomical, 
    close_approach.relative_velocity_kmph
    from training.asteroids
    inner join training.close_approach   
    on asteroids.id = close_approach.neo_reference_id
    where close_approach.astronomical between %s and %s
    and close_approach.miss_distance_lunar between %s and %s
    and close_approach.relative_velocity_kmph between %s and %s
    and asteroids.estimated_diameter_min between %s and %s
    and asteroids.estimated_diameter_max between %s and %s
    and asteroids.is_potentially_hazardous_asteroid between 0 and 1;''')
values=( astronomical[0], astronomical[1], 
        miss_distance_lunar[0], miss_distance_lunar[1], 
        relative_velocity_kmph[0], relative_velocity_kmph[1], 
        estimated_diameter_min[0], estimated_diameter_min[1],
          estimated_diameter_max[0], estimated_diameter_max[1])
cursur.execute(dat,values)
data=cursur.fetchall()
columns=['id','name','is_potentially_hazardous_asteroid','estimated_diameter_min',
    'estimated_diameter_max','absolute_magnitude_h','close_approach_date','miss_distance_km','miss_distance_lunar',
    'astronomical','relative_velocity_kmph']
data_frame=pd.DataFrame(data,columns=columns)

Filter_button=st.button("Filter")

if Filter_button:
    st.dataframe(data_frame.head(10000))

st.snow()
    
Queries = st.sidebar.selectbox("## Queries",["1.Count how many times each asteroid has approached Earth",
"2.Average velocity of each asteroid over multiple approaches",
"3.List top 10 fastest asteroids",
"4.Find potentially hazardous asteroids that have approached Earth more than 3 times",
"5.Find the month with the most asteroid approaches",
"6.Get the asteroid with the fastest ever approach speed",
"7.Sort asteroids by maximum estimated diameter",
"8.Asteroids whose closest approach is getting nearer over time",
"9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth",
"10.List names of asteroids that approached Earth with velocity > 50,000 km/h",
"11.Count how many approaches happened per month",
"12.Find asteroid with the highest brightness",
"13.Get number of hazardous vs non-hazardous asteroids",
"14.Find asteroids that passed closer than the Moon along with their close approach date and distance",
"15.Find asteroids that came within 0.05 AU(astronomical distance)",
"16.Asteroids Within Lunar Distance of Earth",
"17.Count of Hazardous Asteroids",
"18.Hazardous Asteroids Close to Earth"],index=0,placeholder="Select a query")

queries_button=st.sidebar.button("submit")
st.sidebar.write("Select a query or filter to get insights on NEOs")

if queries_button:
    if Queries == "1.Count how many times each asteroid has approached Earth":
        cursur.execute('''select name,count(name) as 'count' from training.asteroids
               group by name;''') 
        astroids_count=cursur.fetchall()
        astroids_count_table=pd.DataFrame(astroids_count,columns=['name','count'])
        st.dataframe(astroids_count_table)
    elif Queries == "2.Average velocity of each asteroid over multiple approaches":
        cursur.execute('''select asteroids.name,
               AVG(close_approach.relative_velocity_kmph) as "avg_velocity"
               from training.asteroids
               inner join training.close_approach 
               on asteroids.id = close_approach.neo_reference_id
               group by asteroids.name
               order by avg_velocity desc;''')
        asteroids_velocity=cursur.fetchall()
        asteroids_velocity_table=pd.DataFrame(asteroids_velocity,columns=['name','avg_velocity'])
        st.dataframe(asteroids_velocity_table)
    elif Queries == "3.List top 10 fastest asteroids":
        cursur.execute('''select asteroids.name,close_approach.relative_velocity_kmph
                from training.asteroids
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                order by close_approach.relative_velocity_kmph desc
                limit 10;''')
        asteroids_velocity=cursur.fetchall()
        asteroids_velocity_table=pd.DataFrame(asteroids_velocity,columns=['name','relative_velocity_kmph'])
        st.dataframe(asteroids_velocity_table)
    elif Queries == "4.Find potentially hazardous asteroids that have approached Earth more than 3 times":
        cursur.execute('''select name,count(name) as 'name_count'
               from training.asteroids
               where is_potentially_hazardous_asteroid = 1 
               group by name
               having name_count > 3;''')
        Danger_astro=cursur.fetchall()
        Danger_astro_table=pd.DataFrame(Danger_astro,columns=['name','Danger_Asteroid_count'])
        st.dataframe(Danger_astro_table)

    elif Queries == "5.Find the month with the most asteroid approaches":
        cursur.execute('''select monthname(close_approach_date) as month,
               count(*) as month_count
               from training.close_approach
               group by monthname(close_approach_date)
               order by month_count desc
               limit 1;''')
        Max_approach_month=cursur.fetchall()
        Max_approach_month_table=pd.DataFrame(Max_approach_month,columns=['month','month_count'])
        st.dataframe(Max_approach_month_table)
    elif Queries == "6.Get the asteroid with the fastest ever approach speed":
        cursur.execute('''select asteroids.name,close_approach.relative_velocity_kmph
                from training.asteroids
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                order by close_approach.relative_velocity_kmph desc
                limit 1;''')
        Max_velocity=cursur.fetchall()
        Max_velocity_table=pd.DataFrame(Max_velocity,columns=['name','Max_velocity'])
        st.dataframe(Max_velocity_table)
    elif Queries == "7.Sort asteroids by maximum estimated diameter":
        cursur.execute('''select name,estimated_diameter_max 
               from training.asteroids
               order by estimated_diameter_max desc;''')
        Maximum_diameter=cursur.fetchall()
        Maximum_diameter_table=pd.DataFrame(Maximum_diameter,columns=['name','Maximum_diameter'])
        st.dataframe(Maximum_diameter_table)
    elif Queries == "8.Asteroids whose closest approach is getting nearer over time":
        cursur.execute('''select asteroids.name,close_approach.close_approach_date,close_approach.miss_distance_km
                from training.asteroids 
               inner join training.close_approach
               on asteroids.id = close_approach.neo_reference_id
               order by close_approach.miss_distance_km desc;''')
        Astroids_comenear_earth=cursur.fetchall()
        Astroids_comenear_earth_table=pd.DataFrame(Astroids_comenear_earth,columns=['name','close_approach_date','miss_distance_km'])
        st.dataframe(Astroids_comenear_earth_table)
    elif Queries == "9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth":
        cursur.execute('''select asteroids.name,close_approach.close_approach_date,close_approach.miss_distance_km
                from training.asteroids 
               inner join training.close_approach
               on asteroids.id = close_approach.neo_reference_id
               order by asteroids.name;''')
        Astroids_comenear_data=cursur.fetchall()
        Astroids_comenear_data_table=pd.DataFrame(Astroids_comenear_data,columns=['name','close_approach_date','miss_distance_km'])
        st.dataframe(Astroids_comenear_data_table)
    elif Queries == "10.List names of asteroids that approached Earth with velocity > 50,000 km/h":
        cursur.execute('''select asteroids.name,close_approach.relative_velocity_kmph
               from training.asteroids 
               inner join training.close_approach
               on asteroids.id = close_approach.neo_reference_id
               where close_approach.relative_velocity_kmph > 50000
               order by close_approach.relative_velocity_kmph desc;''')
        High_velocity=cursur.fetchall()
        High_velocity_table=pd.DataFrame(High_velocity,columns=['name','High_velocity'])
        st.dataframe(High_velocity_table)
    elif Queries == "11.Count how many approaches happened per month":
        cursur.execute('''select monthname(close_approach_date) as month,
               count(*) as month_count
               from training.close_approach
               group by monthname(close_approach_date)
               order by month_count desc;''')
        Max_approach_monthcount=cursur.fetchall()
        Max_approach_monthcount_table=pd.DataFrame(Max_approach_monthcount,columns=['month','month_count'])
        st.dataframe(Max_approach_monthcount_table)
    elif Queries == "12.Find asteroid with the highest brightness":
        cursur.execute('''select asteroids.name,min(asteroids.absolute_magnitude_h) as 'min_absolute_magnitude_h'
               from training.asteroids
               group by asteroids.name
               order by min_absolute_magnitude_h
               limit 1;''')
        Min_absolute_magnitude=cursur.fetchall()
        Min_absolute_magnitude_table=pd.DataFrame(Min_absolute_magnitude,columns=['name','min_absolute_magnitude_h'])
        st.dataframe(Min_absolute_magnitude_table)
    elif Queries == "13.Get number of hazardous vs non-hazardous asteroids":
        cursur.execute('''select asteroids.name,
               count(case when asteroids.is_potentially_hazardous_asteroid = 1 then 1 end) as 'harzardous_count',
               count(case when asteroids.is_potentially_hazardous_asteroid = 0 then 1 end) as 'non_hazardous_count'
               from training.asteroids
              group by asteroids.name;''')
        Hazardous_asteroids=cursur.fetchall()   
        Hazardous_asteroids_table=pd.DataFrame(Hazardous_asteroids,columns=['name','hazardous_count','non_hazardous_count'])
        st.dataframe(Hazardous_asteroids_table)
    elif Queries == "14.Find asteroids that passed closer than the Moon along with their close approach date and distance":
        cursur.execute('''select asteroids.name,close_approach.miss_distance_km,close_approach.close_approach_date
                from training.asteroids 
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                where close_approach.miss_distance_km < 384400;''')
        Asteriods_lessthan_oneLD=cursur.fetchall()
        Asteriods_lessthan_oneLD_table=pd.DataFrame(Asteriods_lessthan_oneLD,columns=['name','miss_distance_km','close_approach_date'])   
        st.dataframe(Asteriods_lessthan_oneLD_table)
    elif Queries == "15.Find asteroids that came within 0.05 AU(astronomical distance)":
        cursur.execute('''select asteroids.name,close_approach.miss_distance_km
                from training.asteroids 
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                where close_approach.miss_distance_km < 7479894;''')
        Asteriods_lessthan_0_05au=cursur.fetchall()
        Asteriods_lessthan_0_05au_table=pd.DataFrame(Asteriods_lessthan_0_05au,columns=['name','miss_distance_km']) 
        st.dataframe(Asteriods_lessthan_0_05au_table)  
    elif Queries == "16.Asteroids Within Lunar Distance of Earth":
        cursur.execute('''select asteroids.name,close_approach.miss_distance_lunar
                from training.asteroids 
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                order by close_approach.miss_distance_lunar;''')
        Astroids_earth_lunar=cursur.fetchall()
        Astroids_earth_lunar_table=pd.DataFrame(Astroids_earth_lunar,columns=['name','miss_distance_lunar'])
        st.dataframe(Astroids_earth_lunar_table)
    elif Queries == "17.Count of Hazardous Asteroids":
        cursur.execute('''select asteroids.name,count(is_potentially_hazardous_asteroid) as 'count'
                from training.asteroids
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                group by asteroids.name,is_potentially_hazardous_asteroid;''')
        Hazardous_asteroids_count=cursur.fetchall() 
        Hazardous_asteroids_count_table=pd.DataFrame(Hazardous_asteroids_count,columns=['name','count'])
        st.dataframe(Hazardous_asteroids_count_table)
    elif Queries == "18.Hazardous Asteroids Close to Earth":
        cursur.execute('''select asteroids.name,asteroids.is_potentially_hazardous_asteroid,close_approach.miss_distance_km,close_approach.close_approach_date
                from training.asteroids 
                inner join training.close_approach
                on asteroids.id = close_approach.neo_reference_id
                where asteroids.is_potentially_hazardous_asteroid = 1
               and close_approach.miss_distance_km < 5000000
               order by close_approach.miss_distance_km;''')
        Hazardous_asteroids_miss_distance=cursur.fetchall()
        Hazardous_asteroids_miss_distance_table=pd.DataFrame(Hazardous_asteroids_miss_distance,columns=['name','is_potentially_hazardous_asteroid','miss_distance_km','close_approach_date'])
        st.dataframe(Hazardous_asteroids_miss_distance_table)
    