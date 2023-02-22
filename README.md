# GoRun

A simple web app to track Strava distance data and set a weekly goal.

This functionality now requires a paid subscription on the Strava app. Also, I've found other applications showing this data to be too complicated.
I wanted a simple page that shows how far I've run and how much further I have to go to get to my weekly target.

This is a web application built using Flask.
Bootstrap was used to style the nav bar, as well as some other elements.

Users can create an account, then authorize their Strava account to allow the application to access their activity data.

The application sends the Oauth authorization requests to Strava, stores the access codes, and handles refreshing the tokens when they expire. This means that
once authorised, the app should keep access to the Strava account until the user chooses to revoke access.

Users can then set a weekly goal. The data page shows how far they've run in the current week, and how far they have left to reach their goal.
You can also see a summary of each day's runs by clicking on the day of week.

Hosted on pythonanywhere at: http://gorunn.eu.pythonanywhere.com/

<br>

<div style="display:flex">
  <img src="/Screenshots/gorun_login.png" style="height:500px" alt="Login page">
  <img src="/Screenshots/gorun_home.png" style="height:500px" alt="Home page">
  <img src="/Screenshots/gorun_home2.png" style="height:500px" alt="Home page 2">
  <img src="/Screenshots/gorun_account.png" style="height:500px" alt="Account page">
  <img src="/Screenshots/gorun_Oauth.png" style="height:500px" alt="Strava Oauth">
</div>
