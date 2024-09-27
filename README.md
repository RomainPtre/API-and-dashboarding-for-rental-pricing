# 🚗 Project Getaround 

In order to mitigate the issue of friction between late return of rentals and the next user, getaround decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental. It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.

---
Most of the EDA is in the Project-8-Get_around notebook, accessible through the repo, and I have included the most relevant infos in the dashboard.

---
## 📊 Dashboard
I have created a dashboard that will help the Product Management Team to select the right threshold for the feature.

**Please find the dashboard (streamlit app) here: https://getaround.streamlit.app/**

All the visualisations and calculations will dynamically adapt to the threshold you select using the main slider.

---

## API

---

---

To deploy locally, run the following command in the terminal (from the api folder):

```uvicorn app:app --reload --host 0.0.0.0 --port 4000```


and open 'http://localhost:4000/' in your browser.

To request prediction from the API given user data : 

In a bash terminal:

```
curl -X POST "http://localhost:4000/predict" \
-H "Content-Type: application/json" \
-d '{"model_key":"Renault","mileage":77334,"engine_power":256,"fuel":"diesel","paint_color":"black","car_type":"coupe","private_parking_available":true,"has_gps":false,"has_air_conditioning":true,"automatic_car":false,"has_getaround_connect":false,"has_speed_regulator":true,"winter_tires":false}'
```

**To fix** Special characters such as 'Citroën' currently not working. Possible to force UTF-8 encoding in the curl command, but this solution is not user friendly. app.py should be fixed accordingly in the futur.

---

To deploy on heroku

