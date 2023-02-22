
//========== Progress circle ===========//

let percentage = document.getElementById('progress_percent').innerHTML;
console.log(percentage); 

percentage = (percentage.substring(0, percentage.length - 1)) / 100;

// Calculate dashoffset value (dasharray - dasharray * percentage)
var dashoffset = 440 - (440 * percentage);

// Set root dashoffset variable
document.documentElement.style.setProperty('--my-dashoffset', dashoffset);



//============= Days of the week ================//

// Change colours - grey for past days, blue for future

const d = new Date();
let day = d.getDay();

if (day == 1) {
    document.getElementById('mon').style.backgroundColor = '#3AE1A4';    
}
if (day == 2) {    
    document.getElementById('tue').style.borderColor = '#000';    
    document.getElementById('mon').style.backgroundColor = '#C9C9C9';    
}
if (day == 3) {
    document.getElementById('mon').style.backgroundColor = '#C9C9C9';    
    document.getElementById('tue').style.backgroundColor = '#C9C9C9';    
}
if (day == 4) {
    document.getElementById('mon').style.backgroundColor = '#C9C9C9';    
    document.getElementById('tue').style.backgroundColor = '#C9C9C9';    
    document.getElementById('wed').style.backgroundColor = '#C9C9C9';    
}
if (day == 5) {
    document.getElementById('mon').style.backgroundColor = '#C9C9C9';    
    document.getElementById('tue').style.backgroundColor = '#C9C9C9';    
    document.getElementById('wed').style.backgroundColor = '#C9C9C9';    
    document.getElementById('thu').style.backgroundColor = '#C9C9C9';    
}
if (day == 6) {
    document.getElementById('mon').style.backgroundColor = '#C9C9C9';    
    document.getElementById('tue').style.backgroundColor = '#C9C9C9';    
    document.getElementById('wed').style.backgroundColor = '#C9C9C9';    
    document.getElementById('thu').style.backgroundColor = '#C9C9C9';    
    document.getElementById('thu').style.backgroundColor = '#C9C9C9';    
}
if (day == 0) {
    document.getElementById('mon').style.backgroundColor = '#C9C9C9';    
    document.getElementById('tue').style.backgroundColor = '#C9C9C9';    
    document.getElementById('wed').style.backgroundColor = '#C9C9C9';    
    document.getElementById('thu').style.backgroundColor = '#C9C9C9';    
    document.getElementById('fri').style.backgroundColor = '#C9C9C9';    
    document.getElementById('sat').style.backgroundColor = '#C9C9C9';    
}


// If day of the week is clicked, show table with that day's runs at the bottom of the page

// Function takes day of the week as variable (0 indexed)
function showHide(d) {
    
    var clicked_day_table = document.getElementById(`data_table_${d}`);
    var clicked_weekday = document.getElementById(`weekday_${d}`);
    var tables = document.getElementsByClassName('table_item');
    
    // If clicked element's display is flex, loop through all elements and change to none

    if (clicked_day_table.style.display == 'flex') {
        for (var i = 0; i < tables.length; i++) {
            tables[i].style.display = 'none';
        }
    }
    // Else, loop through all and set to none. Then set clicked_day_table to flex. 
    else {
        for (var i = 0; i < tables.length; i++) {
            tables[i].style.display = 'none';
        }
    
        clicked_day_table.style.display = 'flex';
        clicked_weekday.style.display = 'flex';

        clicked_day_table.scrollIntoView();
        clicked_day_table.scrollIntoView({behavior: "smooth"});
    }
  } 




